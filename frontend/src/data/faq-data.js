/**
 * FAQ data organized by platform and category.
 * Each FAQ has a question, answer, and tags for search filtering.
 */

const faqData = [
  {
    category: 'Shopify — Store & Products',
    icon: '🛍️',
    items: [
      {
        q: 'How do I add a product to my store?',
        a: 'Go to **Products > Add product** in your Shopify admin. Fill in the title, description, images, pricing, and inventory details. Click **Save** when done. Your product will appear on your storefront if its status is set to "Active" and it\'s added to your Online Store sales channel.',
        tags: ['shopify', 'products', 'add'],
      },
      {
        q: 'Why aren\'t my products showing on my store?',
        a: 'Check these common causes:\n1. **Product status** — Make sure it\'s set to "Active" (not "Draft")\n2. **Sales channel** — Verify the product is available on your "Online Store" channel\n3. **Collections** — Ensure the product is in a collection that\'s displayed on your theme\n4. **Browser cache** — Try hard-refreshing with Ctrl+Shift+R',
        tags: ['shopify', 'products', 'visibility', 'troubleshooting'],
      },
      {
        q: 'How do I set up discount codes?',
        a: 'Go to **Discounts > Create discount** in your Shopify admin. Choose the type (percentage, fixed amount, free shipping, or buy X get Y). Set conditions like minimum purchase, eligible products, usage limits, and active dates. Share the code with customers — they\'ll enter it at checkout.',
        tags: ['shopify', 'discounts', 'coupons'],
      },
      {
        q: 'How do I process a partial refund?',
        a: 'Open the order in **Orders**, click **Refund**, then set the quantity to refund for each item (e.g., 1 out of 3). Shopify auto-calculates the amount. You can optionally refund shipping and choose to restock the returned item. Click **Refund** to process it.',
        tags: ['shopify', 'orders', 'refund'],
      },
    ],
  },
  {
    category: 'Shopify — Shipping & Domains',
    icon: '📦',
    items: [
      {
        q: 'Why don\'t international customers see shipping options?',
        a: 'You need to create international shipping zones. Go to **Settings > Shipping and delivery > Manage rates**. Click **Create shipping zone**, select the countries you ship to, and add shipping rates for that zone (flat rate, calculated, or free).',
        tags: ['shopify', 'shipping', 'international'],
      },
      {
        q: 'How do I connect my custom domain?',
        a: 'Go to **Settings > Domains > Connect existing domain**. At your domain registrar (GoDaddy, Namecheap, etc.), set these DNS records:\n- **A Record**: @ → 23.227.38.65\n- **CNAME**: www → shops.myshopify.com\n\nDNS propagation takes up to 48 hours. Shopify auto-provisions your SSL certificate after.',
        tags: ['shopify', 'domain', 'dns', 'setup'],
      },
    ],
  },
  {
    category: 'Stripe — Payments',
    icon: '💳',
    items: [
      {
        q: 'A customer\'s payment was declined. What should I tell them?',
        a: 'Payment declines are handled by the customer\'s bank, not by us. Common reasons include:\n- **Insufficient funds** — use a different card\n- **Expired card** — update card details\n- **Fraud block** — contact their bank to authorize the transaction\n\nWe cannot see why the bank declined the card. The customer should contact their card issuer for specifics.',
        tags: ['stripe', 'payment', 'declined', 'card'],
      },
      {
        q: 'How long do refunds take to appear?',
        a: 'Refund processing times depend on the payment method:\n- **Credit/debit cards**: 5–10 business days\n- **Bank debits (ACH)**: 3–5 business days\n- **Digital wallets** (Apple Pay, Google Pay): 1–3 business days\n\nThe refund is processed immediately on our end — the delay is with the customer\'s bank.',
        tags: ['stripe', 'refund', 'timeline'],
      },
      {
        q: 'I received a chargeback/dispute. What do I do?',
        a: 'Go to **Payments > Disputes** in the Stripe Dashboard. You have a limited time to respond (shown on the dispute). Upload evidence such as:\n- Delivery confirmation / tracking number\n- Customer communication logs\n- Screenshots of your terms of service\n\nWrite a clear, factual rebuttal and submit before the deadline. Disputes typically take 60–90 days to resolve.',
        tags: ['stripe', 'dispute', 'chargeback'],
      },
      {
        q: 'Why isn\'t my subscription renewing automatically?',
        a: 'Subscriptions can fail to renew due to payment failures. Check the subscription in your dashboard — look for the decline code on the latest invoice. Common fixes:\n- Enable **Smart Retries** to automatically retry failed payments\n- Set up **dunning emails** to notify customers to update their payment method\n- Enable the **Customer Portal** so customers can self-serve their card updates',
        tags: ['stripe', 'subscription', 'renewal', 'failed'],
      },
    ],
  },
  {
    category: 'Twilio — Notifications & Messaging',
    icon: '📱',
    items: [
      {
        q: 'My SMS messages aren\'t being delivered. What\'s wrong?',
        a: 'Check the message status in **Console > Monitor > Messaging Logs**. Common issues:\n- **Error 30007**: Message filtered as spam — register for A2P 10DLC\n- **Error 30003**: Phone is unreachable or turned off\n- **Error 30005**: Invalid number format — use E.164 format (+1XXXXXXXXXX)\n\nAlways include opt-out language ("Reply STOP to unsubscribe") and register your number for 10DLC compliance.',
        tags: ['twilio', 'sms', 'delivery', 'troubleshooting'],
      },
      {
        q: 'Customers aren\'t receiving their verification codes',
        a: 'Check the Verify logs in **Console > Verify > your service > Logs**. Common causes:\n- Customer has Do Not Disturb enabled\n- Number is a VoIP/virtual number (often blocks Verify)\n- Too many attempts triggered rate limiting\n\n**Quick fix**: Enable email as a fallback channel in your Verify service settings, or try WhatsApp delivery.',
        tags: ['twilio', 'verify', '2fa', 'code'],
      },
      {
        q: 'How do I set up shipping notification SMS?',
        a: 'You\'ll need:\n1. A **Twilio phone number** with SMS capability\n2. **A2P 10DLC registration** (required for US business messaging)\n3. A **Messaging Service** with your number attached\n\nYour developer team can then integrate the Twilio API to send notifications when orders ship. Always include tracking links and opt-out language in every message.',
        tags: ['twilio', 'sms', 'notifications', 'shipping'],
      },
    ],
  },
  {
    category: 'Vercel — Website & Deployment',
    icon: '🚀',
    items: [
      {
        q: 'My deployment is failing with a build timeout',
        a: 'Build timeouts usually mean something in your build is taking too long. Try these:\n1. **Clear build cache**: Project Settings > General > Build Cache > Clear\n2. **Remove unused dependencies** from package.json\n3. **Optimize static generation**: Use ISR instead of generating all pages at build time\n\nThe hobby plan has a 45-minute build timeout and 100 builds/day limit.',
        tags: ['vercel', 'deployment', 'build', 'timeout'],
      },
      {
        q: 'My environment variables aren\'t working in production',
        a: 'Common causes:\n1. **Scope**: Check that the variable is enabled for "Production" (not just Preview/Development) in Project Settings > Environment Variables\n2. **Client-side access**: In Next.js, only variables prefixed with `NEXT_PUBLIC_` are available in the browser\n3. **Redeploy needed**: Vercel doesn\'t auto-redeploy when you change env vars — trigger a manual redeploy\n4. **Typos**: Double-check variable names match exactly',
        tags: ['vercel', 'environment', 'variables', 'production'],
      },
      {
        q: 'My API routes are timing out (504 error)',
        a: 'Vercel serverless functions have timeout limits:\n- **Hobby (free)**: 10 seconds\n- **Pro**: 60 seconds\n\nIf your function takes longer, optimize it:\n- Add caching for expensive operations\n- Use connection pooling for databases\n- Move heavy processing to background jobs\n- Consider Edge Functions for faster cold starts',
        tags: ['vercel', 'api', 'timeout', '504'],
      },
      {
        q: 'My custom domain shows "Invalid Configuration"',
        a: 'Your DNS isn\'t pointing to Vercel correctly. Set these records at your domain registrar:\n- **A Record**: @ → 76.76.21.21\n- **CNAME**: www → cname.vercel-dns.com\n\nIf using Cloudflare, set the proxy to **DNS only** (gray cloud). DNS changes take up to 48 hours to propagate.',
        tags: ['vercel', 'domain', 'dns', 'configuration'],
      },
    ],
  },
  {
    category: 'Account & Billing',
    icon: '👤',
    items: [
      {
        q: 'How do I change my Shopify plan?',
        a: 'Go to **Settings > Plan** in your Shopify admin. You can upgrade or downgrade at any time. Upgrades take effect immediately; downgrades take effect at the end of your current billing cycle. Annual billing saves 25% compared to monthly.',
        tags: ['shopify', 'billing', 'plan'],
      },
      {
        q: 'What are the transaction fees?',
        a: 'If using Shopify Payments, there are no additional transaction fees — you only pay the credit card processing rate (2.4%–2.9% + 30¢ depending on your plan). If using a third-party payment gateway, there\'s an additional 0.5%–2% fee on top of the gateway\'s own fees.',
        tags: ['shopify', 'stripe', 'fees', 'billing'],
      },
      {
        q: 'How do I add staff members to my account?',
        a: 'Go to **Settings > Users and permissions > Add staff**. Enter their email and set granular permissions for what they can access (orders, products, reports, etc.). We strongly recommend enabling two-factor authentication (2FA) for all staff accounts.',
        tags: ['shopify', 'staff', 'account', 'permissions'],
      },
    ],
  },
];

export default faqData;
