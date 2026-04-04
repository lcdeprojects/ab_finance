from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_DOWN
import re

class Cliente(models.Model):
    nome = models.CharField("Nome Completo", max_length=255)
    cpf = models.CharField("CPF", max_length=14, unique=True)
    telefone = models.CharField("Telefone", max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.cpf:
            self.cpf = re.sub(r'\D', '', str(self.cpf))
        if self.telefone:
            self.telefone = re.sub(r'\D', '', str(self.telefone))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} ({self.cpf})"

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("Pix", "Pix"),
        ("Cartão", "Cartão"),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="payments", null=True)
    total_value = models.DecimalField("Valor Total", max_digits=10, decimal_places=2)
    down_payment = models.DecimalField("Entrada", max_digits=10, decimal_places=2, default=0)
    down_payment_date = models.DateField("Data da Entrada", default=timezone.now)
    installments = models.PositiveIntegerField("Parcelas", choices=[(i, str(i)) for i in range(1, 13)], default=1)
    installment_value = models.DecimalField("Valor da Parcela", max_digits=10, decimal_places=2, editable=False)
    due_date = models.DateField("Data de Vencimento Inicial")
    payment_method = models.CharField("Método de Pagamento", choices=PAYMENT_METHOD_CHOICES, max_length=100)
    down_payment_is_paid = models.BooleanField("Entrada Paga?", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.installments > 0:
            residual = self.total_value - self.down_payment
            self.installment_value = residual / Decimal(self.installments)
        else:
            self.installment_value = Decimal(0)
        super().save(*args, **kwargs)

    def __str__(self):
        cliente_nome = self.cliente.nome if self.cliente else self.name
        return f"{cliente_nome} - R$ {self.total_value}"

class Installment(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="installment_set")
    number = models.PositiveIntegerField("Número da Parcela")
    value = models.DecimalField("Valor da Parcela", max_digits=10, decimal_places=2)
    paid_value = models.DecimalField("Valor Pago", max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField("Data de Vencimento")
    payment_date = models.DateField("Data do Pagamento", null=True, blank=True)
    is_paid = models.BooleanField("Pago S/N", default=False)
    has_nf = models.BooleanField("NF", default=False)

    @property
    def pending_value(self):
        return self.value - self.paid_value

    @property
    def whatsapp_link(self):
        if not self.payment.cliente or not self.payment.cliente.telefone:
            return "#"
        
        nome = self.payment.cliente.nome
        vencimento = self.due_date.strftime('%d/%m/%Y')
        valor = f"{self.value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        parcela = self.number
        total = self.payment.installments
        telefone = self.payment.cliente.telefone
        
        # Clean phone (ensure 55 prefix if not present and only digits)
        phone_clean = re.sub(r'\D', '', str(telefone))
        if not phone_clean.startswith('55'):
            phone_clean = '55' + phone_clean
            
        if parcela == 0:
            referencia = "Referente à Entrada"
        else:
            referencia = f"Referente a parcela {parcela} de {total}"
            
        message = (
            f"Boa tarde {nome}, como vai?\n\n"
            f"Deixarei abaixo a chave pix do escritório para o depósito dos honorários deste mês, "
            f"que deverá ser pago até o dia {vencimento}\n\n"
            f"Banco Nubank\n"
            f"Arthur Boettcher Sociedade Individual de Advocacia\n"
            f"CNPJ: 61086178000191\n"
            f"R$ {valor}\n\n"
            f"{referencia}\n\n"
            f"A equipe AB Advocacia se coloca a sua disposição para sanar eventuais dúvidas"
        )
        
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{phone_clean}?text={encoded_message}"

    def __str__(self):
        cliente_nome = self.payment.cliente.nome if self.payment.cliente else self.payment.name
        return f"{cliente_nome} - Parcela {self.number}/{self.payment.installments}"

# Signal for automatic generation
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Payment)
def sync_installments(sender, instance, created, **kwargs):
    """
    Syncs installments when a Payment is created or updated.
    Preserves paid installments (is_paid=True).
    Recreates/adjusts unpaid installments (is_paid=False).
    """
    # Get existing paid installments
    paid_installments = instance.installment_set.filter(is_paid=True).order_by('number')
    paid_nums = set(paid_installments.values_list('number', flat=True))
    paid_total = paid_installments.aggregate(models.Sum('value'))['value__sum'] or Decimal('0')
    
    # 1. Delete all UNPAID installments to start fresh for the remaining balance
    instance.installment_set.filter(is_paid=False).delete()
    
    # 2. Handle Entry (#0) if it was NOT paid and down_payment > 0
    if instance.down_payment > 0 and 0 not in paid_nums:
        Installment.objects.create(
            payment=instance,
            number=0,
            value=instance.down_payment,
            due_date=instance.down_payment_date,
            is_paid=instance.down_payment_is_paid,
            payment_date=timezone.now().date() if instance.down_payment_is_paid else None,
            paid_value=instance.down_payment if instance.down_payment_is_paid else 0
        )
        
    # 3. Handle Normal Installments (#1..N)
    normal_paid_count = paid_installments.filter(number__gt=0).count()
    remaining_count = max(0, instance.installments - normal_paid_count)
    
    if remaining_count > 0:
        # Calculate remaining balance: Total - PaidHistory - UnpaidEntrance
        balance = instance.total_value - paid_total
        if 0 not in paid_nums:
             balance -= instance.down_payment
             
        # Value for each remaining unpaid installment
        # We use integer division and then calculate the remainder
        # Or just calculate total and give the difference to the first one
        total_remaining_val = balance.quantize(Decimal('0.01'))
        base_val = (total_remaining_val / Decimal(remaining_count)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        remainder = total_remaining_val - (base_val * Decimal(remaining_count))
        
        # Create missing installments
        created_count = 0
        for i in range(1, 100): # Safe upper bound
            if created_count >= remaining_count:
                break
                
            if i not in paid_nums:
                current_val = base_val
                if created_count == 0:
                    # Give the remainder to the first installment created
                    current_val += remainder
                
                Installment.objects.create(
                    payment=instance,
                    number=i,
                    value=current_val,
                    due_date=instance.due_date + relativedelta(months=i-1)
                )
                created_count += 1
