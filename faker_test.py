import os
import random
from decimal import Decimal

import django
from faker import Faker

# Setup Django BEFORE importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_system.settings')
django.setup()

from core.models import Cliente, Payment

fake = Faker('pt_BR')

def insert_cliente():
   # Inserir cliente
   cliente = Cliente.objects.create(
       nome=fake.name(),
       cpf=fake.cpf(),
       telefone=fake.phone_number()
   )
   
   print(f"Cliente {cliente.nome} inserido com sucesso!")
   return cliente

def insert_payment():
   # Inserir payment
   # Get or create a client first
   cliente = Cliente.objects.all().order_by('?').first()
   if not cliente:
       cliente = insert_cliente()
   
   # Generate random payment data
   total_value = Decimal(str(4000.00))
   down_payment = Decimal(str(1000.00))
   installments = fake.random_int(min=1, max=12)
   down_payment_date = fake.date_between(start_date='-100d', end_date='today')
   
   payment = Payment.objects.create(
       cliente=cliente,
       total_value=total_value,
       down_payment=down_payment,
       installments=installments,
       due_date=fake.date_between(start_date='-100d', end_date='today'),
       payment_method=fake.random_element(elements=("Pix", "Cartão")),
       down_payment_date=down_payment_date,
   )
   
   print(f"Payment {payment.id} inserido com sucesso! Cliente: {payment.cliente.nome}, Valor: R${payment.total_value}")
   return payment


def delete_all():
   Payment.objects.all().delete()
   Cliente.objects.all().delete()
   print("Todos os dados foram deletados.")

if __name__ == "__main__":
   insert_payment()
   