from django.shortcuts import render,redirect
from django.conf import settings
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
# from weasyprint import HTML
from django.http import HttpResponse
from django.http import JsonResponse
from django.db import connection
from django.utils.timezone import now
from transport.models import *
from .models import *
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
def voucher_view(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     
     # raw_query2="""SELECT *
     # FROM payment_voucher
     # WHERE user_id = %s 
     # AND due_date > NOW()
     # AND status_id = (
     #    SELECT status_id 
     #    FROM payment_paymentstatus 
     #    WHERE status_name = 'Pending'
     # )
     # LIMIT 1;
     # """
     # with connection.cursor() as cursor:
     #    cursor.execute(raw_query2, [request.user.appuser.roll_num])
     #    voucher = cursor.fetchone() 
     try:
          voucher = Voucher.objects.get(
          user=request.user.appuser, 
          due_date__gt=now(), 
          status__status_name='Pending'
          )
     except Voucher.DoesNotExist:
          voucher=None
     return render(request, "payment/voucher.html",{"providers":providers,"voucher":voucher,"user":request.user})


# def generate_challan_pdf(request):
#      try:
#           voucher = Voucher.objects.get(
#           user=request.user.appuser, 
#           due_date__gt=now(), 
#           status__status_name='Pending'
#           )
#      except Voucher.DoesNotExist:
#           voucher=None
#           return HttpResponse("Challan not found.", status=404)
     
#      context={"voucher":voucher,"user":request.user}
#      html_string = render_to_string('challan_template.html', context)
#      pdf_file = HTML(string=html_string).write_pdf()
     
#      response = HttpResponse(pdf_file, content_type='application/pdf')
#      response['Content-Disposition'] = f'attachment; filename="challan_{voucher.id}.pdf"'
#      return response
   

       
   
def payment_history_view(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     raw_query2="""SELECT * FROM payment_payment WHERE user_id = %s"""
     payments=Payment.objects.raw(raw_query2,[request.user.appuser.roll_num])
     return render(request, "payment/payment-history.html",{"providers":providers,"payments":payments})

class CreateCheckoutSessionView(View):
     @method_decorator(csrf_protect)
     def post(self,request,*args,**kwargs):
          host = self.request.get_host()
          #YOUR_DOMAIN="http://127.0.0.1:8000"
          voucher = Voucher.objects.get(
               user=self.request.user.appuser, 
               due_date__gt=now(), 
               status__status_name='Pending'
          )
          checkout_session = stripe.checkout.Session.create(
               customer_email=self.request.user.email,
               payment_method_types=['card'],
               line_items=[
               {
                    'price_data':{
                         'currency':'pkr',
                         'unit_amount':voucher.amount * 100,
                         'product_data':{
                              'name':'Fees Voucher',
                         },
                    },
                    'quantity': 1,
               },
          ],
          mode='payment',
          invoice_creation={
               "enabled": True,
          },
          metadata={
               "user_rollnum": self.request.user.appuser.roll_num,  
               "product_name": "Fees Voucher",
          },
          success_url="http://{}{}".format(host,reverse('payment:success')),
          cancel_url="http://{}{}".format(host,reverse('payment:cancel'))
          )
          return redirect(checkout_session.url, code=303)

          
class SuccessView(TemplateView):
     template_name="success.html"
class CancelView(TemplateView):
     template_name="cancel.html"               


@csrf_exempt
def webhook_view(request):
     payload = request.body
     sig_header=request.META['HTTP_STRIPE_SIGNATURE']
     event=None
     
     try:
          event = stripe.Webhook.construct_event(payload,sig_header,settings.STRIPE_WEBHOOK_SECRET)
     except ValueError as e:
          return HttpResponse(status=400)
     except stripe.error.SignatureVerificationError as e:
          return HttpResponse(status=400)
     
     if event['type']=='checkout.session.completed':
          
          session = event['data']['object']
          payment_intent_id = session["payment_intent"]
          user_email = session["customer_email"]

          print(session)
        # Retrieve the Payment Intent from Stripe
          payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        # Extract payment details
          amount = payment_intent["amount_received"]/100
          metadata = session.get("metadata", {})
          user_rollnum = metadata.get("user_rollnum")  # Assuming you pass user_id in metadata
          product_name = metadata.get("product_name")
        # Save Payment and Receipt in the database
          try:
               user = AppUser.objects.get(roll_num=user_rollnum)
            # Create a receipt
               voucher_id=f"{payment_intent_id}{user_rollnum}"
              
               invoice = event["data"]["object"]
               invoice_id = invoice["invoice"]
        
               # Fetch the invoice details to get the invoice URL
               invoice_details = stripe.Invoice.retrieve(invoice_id)
        
               # Get the URL to view the invoice in a browser
               invoice_url = invoice_details["hosted_invoice_url"]

               receipt = Receipt.objects.create(profile_voucher_number=voucher_id,browser_view=invoice_url)
               # Payment status and method
               method, _ = PaymentMethod.objects.get_or_create(method_name="Online")
               
               fees_voucher = Voucher.objects.get(
               user=user, 
               due_date__gt=now(), 
               status__status_name='Pending'
               )

               status=PaymentStatus.objects.get(status_name="Succeeded")
               print(fees_voucher.status)
               print(status)
               fees_voucher.status=status
               fees_voucher.save()

               # Save Payment
               payment = Payment.objects.create(
                    user=user,
                    receipt=receipt,
                    voucher=fees_voucher,
                    method=method,
                    amount=amount,
               )
               
               #Send receipt email
               subject = "Your Invoice from Our Service"
               message = f"Thank you for your payment. You can view your invoice here: {invoice_url}"

               send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])


          except AppUser.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

     return HttpResponse(status=200)
          