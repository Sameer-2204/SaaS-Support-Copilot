"""Generate synthetic support data for e-commerce platforms.

Creates realistic resolved tickets, changelogs, and API error references
for Shopify, Stripe, Twilio, and Vercel using the Groq LLM.

Usage:
    python -m scripts.generate_synthetic_data
    python -m scripts.generate_synthetic_data --platform stripe
    python -m scripts.generate_synthetic_data --type tickets
"""

import json
import os
import sys
import time
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Try to import groq for LLM generation; fall back to templates if unavailable
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# ---------------------------------------------------------------------------
# Pre-built synthetic data templates (used as fallback or seed data)
# ---------------------------------------------------------------------------

RESOLVED_TICKETS = {
    "shopify": [
        {
            "ticket_id": "SHOP-001", "product": "shopify", "category": "store-setup",
            "subject": "Can't add products to my new store",
            "question": "I just created my Shopify store and I'm trying to add my first product but the 'Add product' button doesn't seem to work. I click it and nothing happens. I'm using Chrome on Windows.",
            "resolution": "This is typically caused by a browser extension conflict. Try these steps:\n1. Open Chrome in Incognito mode (Ctrl+Shift+N)\n2. Navigate to your Shopify admin\n3. Try adding a product again\n\nIf it works in Incognito, disable browser extensions one by one to find the culprit. Common conflicts include ad blockers and privacy extensions.\n\nAlternatively, clear your browser cache: Settings > Privacy > Clear Browsing Data > select 'Cached images and files' > Clear Data.",
            "timestamp": "2024-08-15"
        },
        {
            "ticket_id": "SHOP-002", "product": "shopify", "category": "payments",
            "subject": "Customers getting payment declined errors at checkout",
            "question": "Several customers have contacted me saying their payments are being declined at checkout. They say their cards work fine on other websites. This started happening yesterday.",
            "resolution": "Payment declines can happen for several reasons:\n\n1. **Check your Shopify Payments status**: Go to Settings > Payments and verify your account is in good standing\n2. **Review fraud analysis settings**: Settings > Payments > Manage > Fraud prevention. If set too aggressively, legitimate payments may be blocked\n3. **Check for region restrictions**: Ensure you haven't accidentally blocked certain countries\n4. **Test with a test card**: Use Shopify's test mode to verify checkout works\n\nIf the issue persists, check the 'Analytics > Reports > Declined payments' section for specific decline codes. Common codes:\n- 'do_not_honor': Customer should contact their bank\n- 'insufficient_funds': Customer needs more funds\n- 'card_declined': Generic decline, often fraud-related",
            "timestamp": "2024-09-02"
        },
        {
            "ticket_id": "SHOP-003", "product": "shopify", "category": "shipping",
            "subject": "Shipping rates not showing at checkout for international orders",
            "question": "My domestic shipping works fine but when international customers try to check out, they don't see any shipping options. It just says 'no shipping methods available for your address.'",
            "resolution": "International shipping needs to be configured separately:\n\n1. Go to Settings > Shipping and delivery\n2. Under 'Shipping', click 'Manage rates'\n3. Look for your shipping profile — you likely only have 'Domestic' zones\n4. Click 'Create shipping zone' and select the countries/regions you want to ship to\n5. Add shipping rates (flat rate, calculated, or free) for each zone\n\nTip: You can also use Shopify Shipping to get discounted calculated rates from carriers like DHL, UPS, and USPS for international orders.\n\nMake sure each product in your store has a weight set (Products > select product > Shipping section) for calculated rates to work correctly.",
            "timestamp": "2024-09-10"
        },
        {
            "ticket_id": "SHOP-004", "product": "shopify", "category": "themes",
            "subject": "Theme customization changes not saving",
            "question": "I'm trying to customize my Dawn theme — changing colors and fonts — but when I click Save, the changes don't appear on my live store. I've tried multiple times.",
            "resolution": "This usually happens when you're editing a draft/unpublished theme instead of your live theme:\n\n1. Go to Online Store > Themes\n2. Check which theme is marked as 'Current theme' (it will have a green 'Live' badge)\n3. If you've been editing a different theme, click 'Publish' on that theme to make it live\n\nOther possible causes:\n- **Browser cache**: Hard refresh your storefront with Ctrl+Shift+R\n- **CDN cache**: Changes can take 2-5 minutes to propagate\n- **App conflicts**: Some apps inject CSS that overrides theme settings. Try temporarily disabling recently installed apps",
            "timestamp": "2024-09-18"
        },
        {
            "ticket_id": "SHOP-005", "product": "shopify", "category": "orders",
            "subject": "How to process a partial refund for a multi-item order",
            "question": "A customer ordered 3 items but wants to return just 1. How do I refund only that one item without refunding the entire order?",
            "resolution": "You can issue a partial refund directly from the order:\n\n1. Go to Orders and click the order\n2. Click 'Refund' at the top\n3. In the refund page, enter the quantity to refund for each item (set to 1 for the returned item, 0 for the others)\n4. Shopify will auto-calculate the refund amount\n5. Optionally adjust shipping refund if applicable\n6. Choose whether to restock the returned item\n7. Add a reason for the refund (for your records)\n8. Click 'Refund'\n\nThe customer will receive the partial refund to their original payment method. Processing time depends on their bank (typically 5-10 business days).",
            "timestamp": "2024-10-01"
        },
        {
            "ticket_id": "SHOP-006", "product": "shopify", "category": "discounts",
            "subject": "Discount code not applying at checkout",
            "question": "I created a discount code '20OFF' for 20% off but customers say it's not working when they enter it at checkout. It shows 'discount code isn't valid'.",
            "resolution": "Check these common issues with discount codes:\n\n1. **Active dates**: Go to Discounts > select your code. Verify the start date has passed and it hasn't expired\n2. **Usage limits**: Check if you set a 'Maximum number of uses' and it's been reached\n3. **Minimum requirements**: If you set a minimum purchase amount or quantity, customers may not be meeting it\n4. **Customer eligibility**: Check if you restricted it to specific customer segments\n5. **Product/collection scope**: If you limited it to specific products or collections, verify those items are in the cart\n6. **Combination settings**: Check 'Combinations' — some discounts can't be combined with others\n7. **Case sensitivity**: Discount codes are NOT case-sensitive in Shopify, so this shouldn't be the issue\n\nTip: Test the code yourself by placing a test order to see the exact error message.",
            "timestamp": "2024-10-12"
        },
        {
            "ticket_id": "SHOP-007", "product": "shopify", "category": "inventory",
            "subject": "Inventory count showing wrong numbers",
            "question": "My inventory shows 50 units of a product but I know I only have 30 in my warehouse. The numbers are off and I don't know how to fix them.",
            "resolution": "Inventory discrepancies can happen due to several reasons:\n\n**To correct the inventory count:**\n1. Go to Products > Inventory\n2. Find the product/variant\n3. Click on the quantity number\n4. Choose 'Set' (not 'Adjust') and enter the correct count (30)\n5. Save\n\n**To prevent future mismatches:**\n- Enable 'Track quantity' on all products\n- If you use multiple locations, check inventory at each location separately\n- Review the inventory adjustment history: Products > select product > Inventory > View adjustment history\n- If you use a POS or third-party fulfillment, ensure syncing is working properly\n\n**For ongoing accuracy:**\n- Schedule regular inventory audits (monthly recommended)\n- Use barcode scanning if available to reduce manual errors",
            "timestamp": "2024-10-22"
        },
        {
            "ticket_id": "SHOP-008", "product": "shopify", "category": "domain",
            "subject": "Custom domain not connecting — shows 'DNS not pointed' error",
            "question": "I bought a domain from GoDaddy and I'm trying to connect it to my Shopify store. I updated the DNS records but it still shows an error saying DNS is not pointed correctly.",
            "resolution": "DNS propagation can take up to 48 hours. Here's how to verify your setup:\n\n**Required DNS Records at GoDaddy:**\n1. **A Record**: Host = '@', Points to = 23.227.38.65\n2. **CNAME Record**: Host = 'www', Points to = shops.myshopify.com\n\n**Steps to check:**\n1. Log into GoDaddy > DNS Management for your domain\n2. Delete any existing A records for '@' and add the Shopify one\n3. Delete any existing CNAME for 'www' and add the Shopify one\n4. Wait 24-48 hours for propagation\n5. In Shopify: Online Store > Domains > Check status\n\n**Common mistakes:**\n- Having conflicting A records (there should only be one)\n- GoDaddy sometimes has a 'forwarding' setting that conflicts — disable domain forwarding\n- Make sure you're editing DNS for the right domain if you have multiple\n\nYou can check propagation progress at: https://www.whatsmydns.net",
            "timestamp": "2024-11-05"
        },
    ],
    "stripe": [
        {
            "ticket_id": "STRP-001", "product": "stripe", "category": "checkout",
            "subject": "Stripe Checkout session creates but payment doesn't complete",
            "question": "I've integrated Stripe Checkout and the checkout page loads fine, but after the customer enters their card details and clicks Pay, the payment stays in 'incomplete' status. No webhook events fire either.",
            "resolution": "This usually means the payment confirmation step isn't completing. Common causes:\n\n1. **Missing return_url**: Ensure your Checkout Session includes a `success_url` and `cancel_url`. Without these, the redirect after payment fails.\n\n2. **Webhook not configured**: Go to Developers > Webhooks in your Stripe Dashboard and verify your endpoint URL is correct and listening for `checkout.session.completed`\n\n3. **Test mode mismatch**: Verify you're using test keys consistently. Using a live publishable key with a test secret key (or vice versa) causes silent failures.\n\n4. **3D Secure**: If the customer's card requires 3D Secure authentication, ensure your integration handles the `requires_action` status.\n\n**For your technical team:**\n- Check the Stripe Dashboard > Payments for the specific payment attempt\n- Look at the Events tab for any error events\n- Enable Stripe's test card `4000003560000008` to simulate 3D Secure flows",
            "timestamp": "2024-08-20"
        },
        {
            "ticket_id": "STRP-002", "product": "stripe", "category": "refunds",
            "subject": "Customer refund taking too long to appear",
            "question": "I processed a refund for a customer 5 days ago through Stripe but they're saying the money hasn't appeared back in their account. Is there something wrong?",
            "resolution": "Refund processing times vary by payment method and bank:\n\n**Typical refund timelines:**\n- Credit/debit cards: 5-10 business days\n- Bank debits (ACH): 3-5 business days\n- Digital wallets (Apple Pay, Google Pay): 1-3 business days\n\n**What to check:**\n1. Go to Payments > find the payment > verify the refund shows as 'Succeeded' (not 'Pending')\n2. Check if the refund is partial or full\n3. Note the refund date — count business days (exclude weekends/holidays)\n\n**What to tell the customer:**\n- The refund has been processed on our end (provide the refund date)\n- Their bank may take up to 10 business days to post the credit\n- They should check their credit card statement, not just their checking account\n- If it hasn't appeared after 10 business days, they should contact their bank with the refund reference number\n\n**For disputes:** If the customer files a chargeback before the refund posts, it won't double-refund — Stripe handles this automatically.",
            "timestamp": "2024-09-05"
        },
        {
            "ticket_id": "STRP-003", "product": "stripe", "category": "subscriptions",
            "subject": "Subscription not renewing automatically",
            "question": "We have customers on monthly subscriptions but some aren't renewing. They're showing as 'past_due' in Stripe. The customers say they haven't cancelled.",
            "resolution": "Subscriptions can fail to renew due to payment failures:\n\n1. **Check Smart Retries**: Go to Settings > Billing > Subscriptions and emails. Enable 'Smart Retries' if not already on — this automatically retries failed payments using ML-optimized timing.\n\n2. **Review failed payment reasons**: Click on the subscription > see the latest invoice > check the 'Payment attempt' section for the decline code.\n\nCommon decline codes:\n- `card_declined`: Generic — card may be expired or maxed out\n- `expired_card`: Customer needs to update their card\n- `insufficient_funds`: Temporary — Smart Retries will handle this\n\n3. **Set up dunning emails**: Settings > Billing > Subscriptions and emails > enable 'Send emails when payments fail'. This emails customers to update their payment method.\n\n4. **Customer Portal**: Enable the Stripe Customer Portal so customers can self-serve update their payment details: Settings > Billing > Customer portal\n\n5. **Subscription status after failed payment**: By default, subscriptions go to `past_due` after the first failure and `unpaid` or `canceled` after all retry attempts are exhausted (configurable in billing settings).",
            "timestamp": "2024-09-22"
        },
        {
            "ticket_id": "STRP-004", "product": "stripe", "category": "disputes",
            "subject": "Received a chargeback dispute — what do I do?",
            "question": "I just got an email from Stripe saying a customer filed a dispute/chargeback. The charge was legitimate — they received the product. How do I fight this?",
            "resolution": "Chargebacks need to be responded to within the deadline shown in your Stripe Dashboard:\n\n**Steps to respond:**\n1. Go to Payments > Disputes in your Stripe Dashboard\n2. Click on the dispute to see the reason (fraud, product not received, etc.)\n3. Click 'Submit Evidence'\n4. Upload relevant evidence based on the dispute reason:\n\n**For 'Fraudulent' disputes:**\n- Proof of delivery (tracking number + delivery confirmation)\n- Customer communication (emails, chat logs)\n- AVS and CVC match results (shown in the payment details)\n- IP address and device info from the order\n\n**For 'Product not received':**\n- Shipping tracking information showing delivery\n- Delivery confirmation or signature\n- Customer communication acknowledging receipt\n\n5. Write a clear, factual rebuttal in the text field\n6. Submit before the deadline\n\n**Important notes:**\n- Stripe charges a $15 dispute fee (refunded if you win)\n- The dispute process takes 60-90 days\n- Keep your dispute rate below 0.75% to avoid being placed in a monitoring program",
            "timestamp": "2024-10-08"
        },
        {
            "ticket_id": "STRP-005", "product": "stripe", "category": "webhooks",
            "subject": "Webhook events not being received",
            "question": "I set up a webhook endpoint in Stripe to listen for payment events but I'm not receiving any events. I can see payments are being processed in the dashboard.",
            "resolution": "Common causes for webhook delivery failures:\n\n1. **Verify endpoint URL**: Go to Developers > Webhooks. Make sure the URL is publicly accessible (not localhost) and uses HTTPS.\n\n2. **Check endpoint status**: If the endpoint has too many failures, Stripe may disable it. Look for a yellow or red status indicator.\n\n3. **Firewall/security**: Ensure your server allows incoming POST requests from Stripe's IP ranges. Check with your hosting provider.\n\n4. **SSL certificate**: Your HTTPS certificate must be valid and not self-signed.\n\n5. **Response timeout**: Your endpoint must respond with a 2xx status code within 20 seconds. If processing takes longer, return 200 immediately and process asynchronously.\n\n6. **Test with CLI**: Install the Stripe CLI and run:\n   ```\n   stripe listen --forward-to localhost:4242/webhook\n   stripe trigger payment_intent.succeeded\n   ```\n\n7. **Check event logs**: In Developers > Webhooks > select endpoint > 'Webhook attempts' tab shows delivery attempts and response codes.\n\n**Common mistakes:**\n- Forgetting to verify the webhook signature (causes 400 errors)\n- Using test mode webhooks with live mode data\n- Not subscribing to the right events",
            "timestamp": "2024-10-20"
        },
        {
            "ticket_id": "STRP-006", "product": "stripe", "category": "payouts",
            "subject": "Payout schedule changed — money not being deposited",
            "question": "I used to receive payouts every 2 days but now it says my payout schedule changed to manual. I haven't changed any settings. My balance is growing but no payouts are happening.",
            "resolution": "Your payout schedule may have been changed for risk-related reasons:\n\n1. **Check for Stripe notifications**: Look in your email and Stripe Dashboard notifications for any risk or compliance alerts.\n\n2. **Verify payout schedule**: Settings > Payouts > check if it shows 'Manual' instead of 'Automatic'\n\n3. **Common reasons for schedule changes:**\n   - High dispute/chargeback rate\n   - Identity verification needed (Settings > Account details)\n   - High-risk transaction patterns detected\n   - Bank account information needs updating\n\n4. **To resolve:**\n   - Complete any pending identity verification\n   - Respond to any outstanding disputes\n   - Contact Stripe Support directly via the Dashboard (? icon > Contact us)\n   - If everything checks out, you can switch back: Settings > Payouts > Edit payout schedule\n\n5. **For immediate needs**: You can manually trigger a payout from Balance > Pay out funds, if manual payouts are enabled.",
            "timestamp": "2024-11-01"
        },
    ],
    "twilio": [
        {
            "ticket_id": "TWL-001", "product": "twilio", "category": "sms",
            "subject": "SMS messages not being delivered to customers",
            "question": "We're sending order confirmation SMS messages through Twilio but about 30% of them aren't being delivered. The API returns success but customers say they never received the message.",
            "resolution": "SMS delivery issues are common and usually related to carrier filtering:\n\n1. **Check message status**: In the Twilio Console, go to Monitor > Messaging Logs. Look for messages with status 'undelivered' or 'failed'. The error code will tell you why.\n\n2. **Common error codes:**\n   - 30003: Unreachable destination (phone off or number invalid)\n   - 30005: Unknown destination (invalid number format)\n   - 30006: Landline or unreachable carrier\n   - 30007: Carrier violation (message filtered as spam)\n   - 30008: Unknown error\n\n3. **If filtered as spam (30007):**\n   - Register your phone number with The Campaign Registry (TCR) for A2P 10DLC\n   - Use a branded sender ID or short code for high-volume messaging\n   - Avoid spam-trigger words in message content\n   - Include opt-out instructions ('Reply STOP to unsubscribe')\n\n4. **Best practices:**\n   - Always validate phone numbers before sending (use Twilio Lookup API)\n   - Use E.164 format (+1XXXXXXXXXX for US numbers)\n   - Keep messages under 160 characters when possible\n   - Send from a number in the same country as the recipient",
            "timestamp": "2024-08-25"
        },
        {
            "ticket_id": "TWL-002", "product": "twilio", "category": "verify",
            "subject": "Two-factor authentication codes not arriving for customers",
            "question": "We use Twilio Verify for 2FA during checkout. Some customers report that the verification code never arrives. This is blocking them from completing their purchase.",
            "resolution": "Twilio Verify delivery issues can be troubleshooted:\n\n1. **Check Verify logs**: Console > Verify > select your service > Logs. Look for the specific verification attempt.\n\n2. **Common causes:**\n   - Customer has Do Not Disturb or message blocking enabled\n   - Number is a VoIP/virtual number (these sometimes block Verify)\n   - International number without proper formatting\n   - Rate limiting (too many attempts in short period)\n\n3. **Solutions:**\n   - Enable the **Email channel** as a fallback: Verify service settings > Channels > enable Email\n   - Enable **WhatsApp** as an alternative delivery channel\n   - Increase the code validity period if customers need more time\n   - Set a custom code length (6 digits is standard)\n\n4. **For the customer right now:**\n   - Ask them to check their spam/blocked messages folder\n   - Verify they're entering the correct phone number\n   - Try sending to their email instead\n   - Have them wait 60 seconds and request a new code\n\n5. **Enterprise solution**: Consider using Twilio Verify's 'Silent Network Auth' for supported carriers — it verifies the phone automatically without sending a code.",
            "timestamp": "2024-09-12"
        },
        {
            "ticket_id": "TWL-003", "product": "twilio", "category": "messaging",
            "subject": "Getting error 21608 when sending messages",
            "question": "I'm trying to send SMS messages from my Twilio number but keep getting error 21608: 'The Messaging Service SID is not valid.' I didn't change anything in my code.",
            "resolution": "Error 21608 means the Messaging Service SID in your API call doesn't match a valid Messaging Service in your account:\n\n1. **Check your code**: Look for the `MessagingServiceSid` parameter. It should start with 'MG' followed by 32 hex characters.\n\n2. **Verify in Console**: Go to Messaging > Services and confirm the SID exists and is active.\n\n3. **Common causes:**\n   - The Messaging Service was deleted or deactivated\n   - You're using a SID from a different Twilio account/subaccount\n   - Environment variables are pointing to the wrong SID (check your .env file)\n   - Copy-paste error with the SID (extra spaces or missing characters)\n\n4. **Quick fix**: If you don't need Messaging Services, send directly from your phone number:\n   ```\n   // Instead of:\n   messaging_service_sid='MGXXXXXXXX'\n   \n   // Use:\n   from_='+1234567890'  // Your Twilio number\n   ```\n\n5. **If you need Messaging Services**: Create a new one in Console > Messaging > Services > Create Messaging Service, add your phone number to it, and use the new SID.",
            "timestamp": "2024-09-28"
        },
        {
            "ticket_id": "TWL-004", "product": "twilio", "category": "voice",
            "subject": "Incoming calls going straight to voicemail/not routing",
            "question": "We purchased a Twilio phone number for our customer support line but when customers call, nothing happens — it either rings endlessly or goes to a generic voicemail.",
            "resolution": "Incoming calls need to be configured to route somewhere:\n\n1. **Check number configuration**: Console > Phone Numbers > Active Numbers > click your number\n\n2. **Under 'Voice & Fax':**\n   - 'A call comes in' should have a webhook URL pointing to your server\n   - Your server must respond with TwiML instructions (XML that tells Twilio what to do)\n\n3. **Simple TwiML example to forward calls:**\n   ```xml\n   <Response>\n     <Say>Thank you for calling. Please hold while we connect you.</Say>\n     <Dial>+1XXXXXXXXXX</Dial>\n   </Response>\n   ```\n\n4. **If you don't have a server**, use Twilio Studio:\n   - Console > Studio > Create a flow\n   - Use the visual editor to build a call flow (greeting > menu > forward)\n   - Connect the flow to your phone number\n\n5. **Common issues:**\n   - Webhook URL is unreachable (check firewall, ensure HTTPS)\n   - Server returning invalid TwiML or error responses\n   - Number is in a subaccount you're not checking\n   - Webhook timeout (server must respond within 15 seconds)\n\n6. **Testing**: Use the 'Call Log' in Console > Monitor > Calls to see what happened with each call attempt.",
            "timestamp": "2024-10-15"
        },
        {
            "ticket_id": "TWL-005", "product": "twilio", "category": "notifications",
            "subject": "Setting up order notification SMS for our e-commerce store",
            "question": "We want to automatically send SMS notifications to customers when their order ships. How do we set this up with Twilio?",
            "resolution": "Here's how to set up automated shipping notifications:\n\n**1. Get a Twilio Number:**\n- Console > Phone Numbers > Buy a Number\n- Choose a number with SMS capability in your customers' country\n\n**2. Register for A2P 10DLC (US/Canada):**\n- Required for application-to-person messaging\n- Console > Messaging > Compliance > create a brand and campaign\n- Choose 'Delivery Notifications' as your use case\n\n**3. Create a Messaging Service:**\n- Console > Messaging > Services > Create\n- Add your phone number to the service\n- This gives you better deliverability and compliance\n\n**4. Send from your application:**\n```python\nfrom twilio.rest import Client\n\nclient = Client(ACCOUNT_SID, AUTH_TOKEN)\nmessage = client.messages.create(\n    body=f\"Great news! Your order #{order_id} has shipped! \"\n         f\"Track it here: {tracking_url}. \"\n         f\"Reply STOP to opt out.\",\n    messaging_service_sid='MGXXXXXXXX',\n    to=customer_phone  # E.164 format: +14155551234\n)\n```\n\n**5. Best practices:**\n- Always include opt-out language ('Reply STOP')\n- Send only during reasonable hours (9 AM - 9 PM local time)\n- Keep messages concise with a clear tracking link\n- Log message SIDs for delivery tracking",
            "timestamp": "2024-10-30"
        },
    ],
    "vercel": [
        {
            "ticket_id": "VCL-001", "product": "vercel", "category": "deployment",
            "subject": "Deployment failing with 'Build exceeded maximum duration'",
            "question": "My Next.js project was deploying fine until yesterday. Now every deployment fails with 'Build exceeded maximum duration of 45 minutes.' I haven't changed much in my code.",
            "resolution": "Build timeouts usually mean something in your build process is taking too long:\n\n1. **Check build logs**: Go to your project > Deployments > click the failed one > Build Logs. Look for which step is slow.\n\n2. **Common causes:**\n   - A new dependency with a long install time\n   - Large image optimization during build\n   - Generating too many static pages (ISR might help)\n   - Node modules cache corruption\n\n3. **Fixes:**\n   - **Clear build cache**: Project Settings > General > scroll to 'Build Cache' > click 'Clear'\n   - **Optimize dependencies**: Remove unused packages from package.json\n   - **Use incremental builds**: For Next.js, enable ISR instead of SSG for large page counts\n   - **Speed up installs**: Add `--prefer-offline` to your install command\n\n4. **Check resource usage**: Project Settings > General > see your plan's build limits:\n   - Hobby: 45 min timeout, 100 builds/day\n   - Pro: 45 min timeout, 6000 builds/day\n\n5. **If the build is legitimately large**: Consider splitting into multiple projects or using turborepo for monorepo builds.",
            "timestamp": "2024-08-28"
        },
        {
            "ticket_id": "VCL-002", "product": "vercel", "category": "domains",
            "subject": "Custom domain showing 'Invalid Configuration'",
            "question": "I added my custom domain to my Vercel project but it keeps showing 'Invalid Configuration' and my site shows a Vercel error page when I visit the domain.",
            "resolution": "The 'Invalid Configuration' error means DNS isn't properly pointed to Vercel:\n\n**Step 1: Check your DNS settings at your domain registrar**\n\nFor apex domain (example.com):\n- Type: A Record\n- Name: @ (or empty)\n- Value: 76.76.21.21\n\nFor www subdomain:\n- Type: CNAME\n- Name: www\n- Value: cname.vercel-dns.com\n\n**Step 2: Verify in Vercel**\n1. Go to Project Settings > Domains\n2. Check for any error messages next to your domain\n3. Look for the recommended DNS configuration\n\n**Step 3: Wait for propagation**\n- DNS changes take 24-48 hours to fully propagate\n- Check progress at whatsmydns.net\n\n**Common mistakes:**\n- Having conflicting DNS records (delete old A records)\n- Using Cloudflare proxy (orange cloud) — set it to DNS-only (gray cloud) for Vercel\n- Domain registrar lock preventing changes\n- DNSSEC enabled but misconfigured",
            "timestamp": "2024-09-15"
        },
        {
            "ticket_id": "VCL-003", "product": "vercel", "category": "environment",
            "subject": "Environment variables not available in my deployed app",
            "question": "I added environment variables in the Vercel dashboard but my app can't access them. They work fine locally but return undefined in production.",
            "resolution": "Environment variable issues are one of the most common deployment problems:\n\n1. **Check variable scope**: In Project Settings > Environment Variables, verify the variable is enabled for the correct environment (Production, Preview, Development).\n\n2. **Client vs server side (Next.js):**\n   - Variables starting with `NEXT_PUBLIC_` are available in the browser\n   - All other variables are ONLY available on the server (API routes, getServerSideProps)\n   - If you need a variable in client-side code, prefix it with `NEXT_PUBLIC_`\n\n3. **Redeploy after adding variables**: Vercel doesn't automatically redeploy when you add/change env vars. You need to manually trigger a redeploy.\n\n4. **Verify the variable is set**: Use the Vercel CLI:\n   ```\n   vercel env ls\n   ```\n\n5. **In your app, add a debug endpoint** (remove after testing):\n   ```javascript\n   // pages/api/debug-env.js\n   export default function handler(req, res) {\n     res.json({ hasKey: !!process.env.YOUR_VAR_NAME });\n   }\n   ```\n\n6. **Common mistakes:**\n   - Typos in variable names\n   - Using single quotes around values in the dashboard (don't)\n   - Having a local .env file that masks the issue during development",
            "timestamp": "2024-10-05"
        },
        {
            "ticket_id": "VCL-004", "product": "vercel", "category": "serverless",
            "subject": "API routes timing out with 504 GATEWAY_TIMEOUT",
            "question": "My API routes work locally but when deployed to Vercel, they timeout with a 504 error. The request just hangs for about 10 seconds and then fails.",
            "resolution": "Vercel Serverless Functions have timeout limits based on your plan:\n\n**Timeout limits:**\n- Hobby (free): 10 seconds\n- Pro: 60 seconds\n- Enterprise: 900 seconds\n\n**Diagnosis:**\n1. Check your API route's execution time locally — if it takes >10s, it will timeout on Hobby\n2. Go to Project > Functions tab to see function execution metrics\n\n**Solutions:**\n1. **Optimize your code**: Reduce database query times, add caching, minimize external API calls\n2. **Use Edge Functions** for faster cold starts:\n   ```javascript\n   export const config = { runtime: 'edge' };\n   ```\n3. **Background processing**: For long tasks, return immediately and process in the background using:\n   - Vercel Cron Jobs\n   - A queue service (Upstash, SQS)\n   - Webhook callbacks\n\n4. **Connection pooling**: If connecting to a database, use a connection pooler to avoid cold start connection delays\n\n5. **Upgrade plan**: If your function legitimately needs >10s, Pro plan gives you 60s\n\n6. **Cold start optimization**: Minimize function bundle size by avoiding large dependencies",
            "timestamp": "2024-10-18"
        },
        {
            "ticket_id": "VCL-005", "product": "vercel", "category": "preview",
            "subject": "Preview deployments not working for pull requests",
            "question": "I'm not getting preview deployments when I create pull requests on GitHub. It used to work but now PRs don't trigger any Vercel deployments.",
            "resolution": "Preview deployments depend on proper GitHub integration:\n\n1. **Check Git integration**: Project Settings > Git > verify your GitHub repository is connected and shows the correct repo.\n\n2. **Check ignored build step**: Project Settings > Git > 'Ignored Build Step' — if you added a command here, it might be returning exit code 0 (skip) for branches.\n\n3. **Check branch configuration**: Project Settings > Domains > ensure 'Preview' domains are enabled.\n\n4. **Verify GitHub App permissions**: Go to GitHub > Settings > Applications > Vercel > ensure it has access to the repository.\n\n5. **Re-authorize if needed**: Sometimes the GitHub-Vercel connection becomes stale. Disconnect and reconnect: Project Settings > Git > Disconnect > Reconnect.\n\n6. **Check for deployment limits**: Hobby plan has 100 deployments per day. If you've exceeded this, deployments will be queued.\n\n7. **Check build filters**: If you use `vercel.json` with `builds` or `ignoreCommand`, these might be filtering out certain branches.\n\n**Quick test**: Try pushing a commit directly to the PR branch and check the Vercel dashboard for any deployment activity.",
            "timestamp": "2024-11-02"
        },
    ],
}

CHANGELOGS = {
    "shopify": [
        {"id": "cl_shop_001", "product": "shopify", "version": "Winter 2025", "date": "2025-01-15", "category": "platform", "title": "Shopify Winter 2025 Edition — AI-Powered Store Management", "description": "Shopify introduces AI-powered product description generator, automated inventory forecasting, and enhanced checkout customization. Merchants can now use Shopify Magic to generate SEO-optimized product descriptions from photos.", "breaking_changes": [], "migration_notes": "No migration needed. New features are opt-in from the admin dashboard."},
        {"id": "cl_shop_002", "product": "shopify", "version": "2024.12", "date": "2024-12-01", "category": "checkout", "title": "One-Page Checkout Redesign", "description": "Complete redesign of the checkout experience. Single-page checkout reduces friction and improves conversion rates by up to 15%. Custom checkout UI extensions are now supported for Plus merchants.", "breaking_changes": ["Legacy checkout.liquid customizations will be deprecated by March 2025"], "migration_notes": "Migrate checkout customizations to Checkout UI extensions. See migration guide at shopify.dev/docs/checkout-migration."},
        {"id": "cl_shop_003", "product": "shopify", "version": "2024.11", "date": "2024-11-15", "category": "shipping", "title": "Enhanced Shipping Rate Calculator", "description": "Real-time shipping rate calculation now supports more carriers including FedEx Ground, DHL Express, and regional carriers. Merchants can set delivery promises and display estimated delivery dates at checkout.", "breaking_changes": [], "migration_notes": "Enable in Settings > Shipping and delivery > Carrier accounts."},
        {"id": "cl_shop_004", "product": "shopify", "version": "2024.10", "date": "2024-10-01", "category": "payments", "title": "Shopify Payments — New Payment Methods", "description": "Added support for Buy Now Pay Later (BNPL) through Shop Pay Installments, Klarna, and Afterpay. Automatic currency conversion for international orders now available on all plans.", "breaking_changes": [], "migration_notes": "BNPL options appear automatically at checkout. Disable specific providers in Settings > Payments."},
    ],
    "stripe": [
        {"id": "cl_strp_001", "product": "stripe", "version": "2024-12-18.acacia", "date": "2024-12-18", "category": "api", "title": "API Version 2024-12-18.acacia", "description": "New API version with enhanced subscription scheduling, improved webhook delivery reliability, and expanded support for 25+ additional payment methods across 45 new countries.", "breaking_changes": ["PaymentIntent.charges field is now expandable only (not included by default)", "Customer.sources is deprecated — use PaymentMethods API instead"], "migration_notes": "Pin your API version in your Stripe Dashboard. Test against the new version using test mode before upgrading."},
        {"id": "cl_strp_002", "product": "stripe", "version": "2024-11-01", "date": "2024-11-01", "category": "checkout", "title": "Stripe Checkout — Embedded Mode Improvements", "description": "Embedded Checkout now supports custom fonts, colors, and layout options. New 'payment element' mode allows full control over the checkout form while maintaining PCI compliance.", "breaking_changes": [], "migration_notes": "Update your Stripe.js to v4.x for new embedded mode features."},
        {"id": "cl_strp_003", "product": "stripe", "version": "2024-10-15", "date": "2024-10-15", "category": "billing", "title": "Revenue Recovery — Smart Retries 2.0", "description": "Enhanced machine learning model for automatic payment retries. Now recovers up to 40% more failed subscription payments. Includes new dunning email templates and customer payment update portal.", "breaking_changes": [], "migration_notes": "Smart Retries 2.0 is enabled automatically. Customize retry settings in Dashboard > Settings > Billing."},
        {"id": "cl_strp_004", "product": "stripe", "version": "2024-09-01", "date": "2024-09-01", "category": "security", "title": "Enhanced Radar Fraud Protection Rules", "description": "New custom fraud rules builder with visual rule editor. Support for velocity checks, IP reputation scoring, and device fingerprinting. Machine learning model updated with latest fraud patterns.", "breaking_changes": [], "migration_notes": "Access new rules at Dashboard > Radar > Rules. Existing rules are preserved."},
    ],
    "twilio": [
        {"id": "cl_twl_001", "product": "twilio", "version": "2024-12", "date": "2024-12-01", "category": "messaging", "title": "Rich Content Messaging (RCS) Support", "description": "Send rich messages with carousels, quick reply buttons, and media cards via RCS (Rich Communication Services). Supported on Android devices in 30+ countries. Falls back to SMS automatically.", "breaking_changes": [], "migration_notes": "RCS is available through the existing Messaging API. Add 'ContentSid' parameter to enable rich content."},
        {"id": "cl_twl_002", "product": "twilio", "version": "2024-11", "date": "2024-11-15", "category": "verify", "title": "Twilio Verify — Silent Network Authentication", "description": "Verify phone numbers silently using the cellular network — no SMS or code needed. Reduces friction for mobile app authentication. Supports T-Mobile, AT&T, and Verizon in the US.", "breaking_changes": [], "migration_notes": "Enable Silent Network Auth in your Verify Service settings. Requires SDK update."},
        {"id": "cl_twl_003", "product": "twilio", "version": "2024-10", "date": "2024-10-01", "category": "compliance", "title": "10DLC Campaign Registration Streamlined", "description": "Simplified A2P 10DLC registration process. Self-service brand and campaign registration now takes minutes instead of days. Auto-approval for standard use cases (notifications, 2FA, alerts).", "breaking_changes": ["Unregistered numbers will have reduced throughput (1 msg/sec) starting January 2025"], "migration_notes": "Register your brand and campaigns at Console > Messaging > Compliance before January 2025."},
        {"id": "cl_twl_004", "product": "twilio", "version": "2024-09", "date": "2024-09-15", "category": "platform", "title": "Twilio Segment Integration — Unified Customer Profiles", "description": "Native integration with Twilio Segment for unified customer profiles. Send personalized messages based on real-time customer behavior, purchase history, and engagement patterns.", "breaking_changes": [], "migration_notes": "Connect Segment from Console > Integrations. Requires a Segment account."},
    ],
    "vercel": [
        {"id": "cl_vcl_001", "product": "vercel", "version": "2024-12", "date": "2024-12-01", "category": "platform", "title": "Vercel Fluid Compute — Smarter Serverless", "description": "New compute model that automatically adjusts function concurrency and resource allocation. Functions can now handle multiple requests concurrently, reducing cold starts by up to 80%.", "breaking_changes": [], "migration_notes": "Opt-in via vercel.json: { \"functions\": { \"**/*.js\": { \"supportsMultipleRequests\": true } } }"},
        {"id": "cl_vcl_002", "product": "vercel", "version": "2024-11", "date": "2024-11-15", "category": "framework", "title": "Next.js 15 Support — Turbopack Stable", "description": "Full support for Next.js 15 with stable Turbopack bundler. 10x faster builds and 4x faster development hot module replacement. Partial Prerendering (PPR) now stable.", "breaking_changes": ["Minimum Node.js version is now 18.18.0"], "migration_notes": "Update next to 15.x. See the Next.js upgrade guide for breaking changes."},
        {"id": "cl_vcl_003", "product": "vercel", "version": "2024-10", "date": "2024-10-01", "category": "security", "title": "Vercel Firewall — DDoS Protection & WAF", "description": "Built-in Web Application Firewall with managed rulesets for common attack patterns. Custom rules support IP-based, geo-based, and rate-limiting protections. Automatic DDoS mitigation on all plans.", "breaking_changes": [], "migration_notes": "Firewall is enabled by default. Customize rules in Project Settings > Security."},
        {"id": "cl_vcl_004", "product": "vercel", "version": "2024-09", "date": "2024-09-15", "category": "analytics", "title": "Vercel Web Analytics — Core Web Vitals Dashboard", "description": "Real-time Core Web Vitals monitoring with LCP, FID, CLS, and INP tracking. Page-level performance breakdown with recommendations. Integrates with Speed Insights for actionable optimization suggestions.", "breaking_changes": [], "migration_notes": "Enable in Project Settings > Analytics. Add the @vercel/analytics package to your app."},
    ],
}

API_ERRORS = {
    "shopify": [
        {"id": "err_shop_001", "product": "shopify", "error_code": "401", "http_status": 401, "message": "Unauthorized — Invalid API credentials", "description": "Your API key or access token is invalid, expired, or doesn't have the required permissions for this operation.", "common_causes": ["API key was regenerated but not updated in your app", "Access token expired (private app tokens don't expire, but custom app tokens do)", "App doesn't have the required access scope for this endpoint"], "resolution_steps": ["Verify your API credentials in the Shopify Admin > Apps > your app", "Check that your app has the required access scopes", "If using a custom app, regenerate the access token", "Ensure you're using the correct store URL in your API calls"]},
        {"id": "err_shop_002", "product": "shopify", "error_code": "422", "http_status": 422, "message": "Unprocessable Entity — Validation Error", "description": "The request body contains invalid data. Shopify could not process the entity due to validation errors.", "common_causes": ["Required fields missing (e.g., product title, variant price)", "Invalid data types (e.g., string instead of number for price)", "Duplicate values (e.g., SKU already exists)", "Exceeding field length limits"], "resolution_steps": ["Check the error response body for specific field-level errors", "Review the Shopify API documentation for required fields", "Validate your data before sending to the API", "For product imports, use the bulk operations API for better error handling"]},
        {"id": "err_shop_003", "product": "shopify", "error_code": "429", "http_status": 429, "message": "Too Many Requests — Rate Limited", "description": "You've exceeded the API rate limit. Shopify uses a leaky bucket algorithm: 40 requests per app per store, with a leak rate of 2 per second.", "common_causes": ["Making too many API calls in rapid succession", "Not implementing proper rate limiting in your integration", "Multiple processes making concurrent API calls to the same store"], "resolution_steps": ["Check the 'X-Shopify-Shop-Api-Call-Limit' header in responses", "Implement exponential backoff when you receive a 429", "Use bulk operations API for large data operations", "Batch operations where possible (e.g., GraphQL bulk mutations)", "Consider using webhooks instead of polling for data changes"]},
    ],
    "stripe": [
        {"id": "err_strp_001", "product": "stripe", "error_code": "card_declined", "http_status": 402, "message": "Payment Required — Card Declined", "description": "The customer's card was declined by the card issuer. The specific decline reason is provided in the decline_code field.", "common_causes": ["Insufficient funds on the card", "Card reported lost or stolen", "Card expired", "Incorrect CVC code", "Fraud prevention by the issuing bank"], "resolution_steps": ["Check the decline_code in the error response for the specific reason", "For 'insufficient_funds': customer needs to use a different card", "For 'expired_card': customer needs to update their card details", "For 'incorrect_cvc': ask customer to re-enter their card details", "For 'generic_decline': customer should contact their bank", "Consider implementing Stripe's Adaptive Acceptance for automatic retries"]},
        {"id": "err_strp_002", "product": "stripe", "error_code": "resource_missing", "http_status": 404, "message": "Not Found — Resource Missing", "description": "The requested resource (customer, payment intent, subscription, etc.) does not exist or cannot be found with the provided ID.", "common_causes": ["Using a test mode ID in live mode (or vice versa)", "The resource was deleted", "Typo in the resource ID", "Using an ID from a different Stripe account"], "resolution_steps": ["Verify you're using the correct API keys (test vs live)", "Check the resource ID format (e.g., 'pi_' for PaymentIntents, 'cus_' for Customers)", "Search for the resource in the Stripe Dashboard", "If migrating between test and live, remember resources don't transfer between modes"]},
        {"id": "err_strp_003", "product": "stripe", "error_code": "webhook_signature_verification_failed", "http_status": 400, "message": "Bad Request — Webhook Signature Verification Failed", "description": "The webhook event signature does not match. This can indicate the event was tampered with or the wrong signing secret is being used.", "common_causes": ["Using the wrong webhook signing secret", "Reading the request body before verification (body was modified)", "Using a signing secret from a different webhook endpoint", "Clock skew between your server and Stripe (timestamp tolerance is 300 seconds)"], "resolution_steps": ["Get the correct signing secret from Dashboard > Developers > Webhooks > select endpoint > Signing secret", "Ensure you're reading the raw request body (not parsed JSON) for verification", "Use the Stripe SDK's built-in verification: stripe.webhooks.constructEvent(body, sig, secret)", "If using Express.js, use express.raw() middleware for the webhook route", "Test locally with the Stripe CLI: stripe listen --forward-to localhost:4242/webhook"]},
    ],
    "twilio": [
        {"id": "err_twl_001", "product": "twilio", "error_code": "21211", "http_status": 400, "message": "Invalid 'To' Phone Number", "description": "The 'To' phone number is not a valid phone number. Twilio requires numbers in E.164 format.", "common_causes": ["Number not in E.164 format (missing country code)", "Number contains spaces, dashes, or parentheses", "Invalid country code", "Number is too short or too long for the country"], "resolution_steps": ["Format all numbers in E.164: +[country code][number] (e.g., +14155551234)", "Remove all non-numeric characters except the leading +", "Use the Twilio Lookup API to validate numbers before sending", "For US numbers: +1 followed by 10 digits", "For UK numbers: +44 followed by 10 digits (dropping the leading 0)"]},
        {"id": "err_twl_002", "product": "twilio", "error_code": "21610", "http_status": 400, "message": "Message Blocked — Opt-Out", "description": "The recipient has opted out of receiving messages by replying STOP to a previous message from your number.", "common_causes": ["Customer previously replied STOP to opt out", "Number was previously used by another business and contacts opted out", "Regulatory compliance blocking"], "resolution_steps": ["Respect the opt-out — do not attempt to send to this number again", "If the customer wants to re-subscribe, they must text START to your number", "Review your opt-out list: Console > Messaging > Opt-Out Management", "Implement proper opt-in/opt-out flows in your application", "Include opt-out instructions in every message: 'Reply STOP to unsubscribe'"]},
        {"id": "err_twl_003", "product": "twilio", "error_code": "20003", "http_status": 401, "message": "Authentication Error", "description": "Your Account SID or Auth Token is invalid. Twilio could not authenticate the request.", "common_causes": ["Auth Token was recently rotated but not updated in your app", "Using Account SID from a subaccount with the main account's Auth Token", "Credentials contain leading/trailing whitespace", "Using API Keys instead of Account SID/Auth Token (different format)"], "resolution_steps": ["Find your credentials at Console > Account > General Settings", "Check for whitespace in your environment variables", "If you recently rotated your Auth Token, update all services immediately", "For subaccounts, use the subaccount's own SID and Auth Token pair", "Consider using API Keys for better security and easier rotation"]},
    ],
    "vercel": [
        {"id": "err_vcl_001", "product": "vercel", "error_code": "FUNCTION_INVOCATION_TIMEOUT", "http_status": 504, "message": "Gateway Timeout — Function Invocation Timeout", "description": "The Serverless Function did not respond within the timeout limit. Hobby plan: 10s, Pro: 60s.", "common_causes": ["Database query taking too long", "External API call timing out", "Infinite loop or deadlock in function code", "Cold start + heavy computation exceeding timeout"], "resolution_steps": ["Add request timeouts to all external API calls (set to 5s for Hobby)", "Optimize database queries — add indexes, reduce query complexity", "Use Edge Functions for faster cold starts: export const config = { runtime: 'edge' }", "Move heavy processing to background jobs (Vercel Cron, queue service)", "Check function logs: Project > Functions > select function > Logs", "Consider upgrading to Pro for 60s timeout if optimization isn't sufficient"]},
        {"id": "err_vcl_002", "product": "vercel", "error_code": "FUNCTION_PAYLOAD_TOO_LARGE", "http_status": 413, "message": "Payload Too Large — Request body exceeds limit", "description": "The request or response body exceeds the maximum size limit for Serverless Functions (4.5 MB for request, 4.5 MB for response).", "common_causes": ["Uploading large files through an API route", "API response returning too much data", "Base64-encoded images in the request/response body", "Fetching and returning large datasets without pagination"], "resolution_steps": ["For file uploads: use direct-to-storage uploads (Vercel Blob, S3 presigned URLs)", "Paginate large data responses", "Compress response data (gzip is handled automatically by Vercel)", "For images: use Vercel Image Optimization instead of passing raw image data", "Use streaming responses for large payloads: return new ReadableStream()"]},
        {"id": "err_vcl_003", "product": "vercel", "error_code": "DEPLOYMENT_NOT_FOUND", "http_status": 404, "message": "Not Found — Deployment does not exist", "description": "The requested deployment URL does not correspond to any existing deployment in your project.", "common_causes": ["Old deployment URL that has been cleaned up", "Deployment was deleted or failed", "Using a preview URL from a deleted branch", "Project was removed and recreated with the same name"], "resolution_steps": ["Check your project's Deployments tab for the current active deployment", "If using preview URLs, verify the branch/PR still exists", "Use your custom domain or the production deployment URL instead", "For automated systems: use the Vercel API to fetch the latest deployment URL", "Check if the deployment is in a different team/account"]},
    ],
}


def save_json(data, filepath):
    """Save data as JSON."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    size_kb = os.path.getsize(filepath) / 1024
    print(f"  💾 Saved {len(data)} items → {filepath} ({size_kb:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic support data")
    parser.add_argument(
        "--platform",
        choices=["shopify", "stripe", "twilio", "vercel", "all"],
        default="all",
        help="Platform to generate data for (default: all)",
    )
    parser.add_argument(
        "--type",
        choices=["tickets", "changelogs", "errors", "all"],
        default="all",
        help="Type of data to generate (default: all)",
    )
    args = parser.parse_args()

    platforms = (
        ["shopify", "stripe", "twilio", "vercel"]
        if args.platform == "all"
        else [args.platform]
    )
    data_types = (
        ["tickets", "changelogs", "errors"]
        if args.type == "all"
        else [args.type]
    )

    print(f"\n{'='*60}")
    print(f"  Generating synthetic data for: {', '.join(platforms)}")
    print(f"  Types: {', '.join(data_types)}")
    print(f"{'='*60}")

    # Generate resolved tickets
    if "tickets" in data_types:
        print("\n--- Resolved Tickets ---")
        all_tickets = []
        for platform in platforms:
            tickets = RESOLVED_TICKETS.get(platform, [])
            all_tickets.extend(tickets)
            print(f"  {platform}: {len(tickets)} tickets")

        save_json(all_tickets, os.path.join(DATA_DIR, "resolved_tickets", "tickets.json"))

    # Generate changelogs
    if "changelogs" in data_types:
        print("\n--- Changelogs ---")
        all_changelogs = []
        for platform in platforms:
            entries = CHANGELOGS.get(platform, [])
            all_changelogs.extend(entries)
            print(f"  {platform}: {len(entries)} changelog entries")

        save_json(all_changelogs, os.path.join(DATA_DIR, "changelogs", "changelog_2024.json"))

    # Generate API errors
    if "errors" in data_types:
        print("\n--- API Error References ---")
        all_errors = []
        for platform in platforms:
            errors = API_ERRORS.get(platform, [])
            all_errors.extend(errors)
            print(f"  {platform}: {len(errors)} error references")

        save_json(all_errors, os.path.join(DATA_DIR, "api_errors", "errors.json"))

    # Summary
    print(f"\n{'='*60}")
    total = 0
    if "tickets" in data_types:
        t = sum(len(RESOLVED_TICKETS.get(p, [])) for p in platforms)
        total += t
        print(f"  Resolved tickets: {t}")
    if "changelogs" in data_types:
        c = sum(len(CHANGELOGS.get(p, [])) for p in platforms)
        total += c
        print(f"  Changelogs: {c}")
    if "errors" in data_types:
        e = sum(len(API_ERRORS.get(p, [])) for p in platforms)
        total += e
        print(f"  API errors: {e}")
    print(f"  Total: {total} items")
    print(f"{'='*60}")

    print("\nNext steps:")
    print("  1. Run: python -m scripts.fetch_ecommerce_docs  (if not done)")
    print("  2. Run: python -m scripts.ingest")
    print("  3. Run: python -m scripts.embed_and_store")
    print("  4. Run: python -m scripts.build_bm25")


if __name__ == "__main__":
    main()
