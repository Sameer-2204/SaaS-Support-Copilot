/**
 * Interactive tutorial/guide data for the Tutorials page.
 * Each tutorial has steps with detailed instructions.
 */

const tutorialsData = [
  {
    id: 'shopify-first-sale',
    platform: 'Shopify',
    icon: '🛍️',
    title: 'Get Your First Sale on Shopify',
    description: 'A step-by-step guide to setting up your store and making your first sale.',
    difficulty: 'Beginner',
    estimatedTime: '30 min',
    color: '#22c55e',
    steps: [
      {
        title: 'Set Up Your Store',
        content: 'Go to **shopify.com** and create your account. Choose a store name that reflects your brand. During onboarding, Shopify will ask about your business type and products — answer these to get personalized recommendations.',
      },
      {
        title: 'Choose & Customize Your Theme',
        content: 'Go to **Online Store > Themes**. Start with the free **Dawn** theme — it\'s fast and mobile-optimized. Click **Customize** to adjust colors, fonts, and layout. Upload your logo in the Header section.',
      },
      {
        title: 'Add Your First Product',
        content: 'Navigate to **Products > Add product**. Write a compelling title and description. Upload at least 3 high-quality photos. Set your price and inventory count. Add relevant tags for searchability.',
      },
      {
        title: 'Configure Payments',
        content: 'Go to **Settings > Payments** and activate **Shopify Payments**. This enables credit cards, Apple Pay, and Google Pay. No additional transaction fees apply when using Shopify Payments.',
      },
      {
        title: 'Set Up Shipping',
        content: 'Go to **Settings > Shipping and delivery**. Create shipping rates for your domestic zone. Consider offering free shipping above a minimum order value — this increases average order size.',
      },
      {
        title: 'Launch & Share',
        content: 'Remove the store password in **Online Store > Preferences**. Choose your Shopify plan. Share your store link on social media and send it to friends and family. Your first sale is just around the corner!',
      },
    ],
  },
  {
    id: 'stripe-payment-issues',
    platform: 'Stripe',
    icon: '💳',
    title: 'Troubleshooting Payment Failures',
    description: 'How to diagnose and resolve common payment processing issues.',
    difficulty: 'Intermediate',
    estimatedTime: '15 min',
    color: '#8b5cf6',
    steps: [
      {
        title: 'Check the Decline Code',
        content: 'When a payment fails, Stripe provides a decline code. Go to **Payments** in your Stripe Dashboard and click the failed payment. Common codes:\n- **card_declined**: The bank declined the charge\n- **insufficient_funds**: Not enough money on the card\n- **expired_card**: The card has expired',
      },
      {
        title: 'Verify Card Details',
        content: 'Ask the customer to double-check:\n- Card number (no typos)\n- Expiration date (not expired)\n- CVC/CVV code\n- Billing address matches the one on file with their bank',
      },
      {
        title: 'Check for Fraud Blocks',
        content: 'Stripe Radar may block legitimate payments. Go to **Payments > the failed payment > Risk insights** to see the Radar score. If it\'s a false positive, you can create an allow rule for the customer.',
      },
      {
        title: 'Enable Smart Retries',
        content: 'For recurring payments, enable **Smart Retries** in **Settings > Subscriptions**. Stripe will automatically retry failed payments at optimal times, recovering up to 38% of failed subscription payments.',
      },
      {
        title: 'Set Up Dunning Emails',
        content: 'Configure automatic emails to notify customers when their payment fails. Go to **Settings > Subscriptions > Manage failed payments**. Set up email reminders at 1, 3, and 7 days after failure.',
      },
    ],
  },
  {
    id: 'twilio-sms-setup',
    platform: 'Twilio',
    icon: '📱',
    title: 'Setting Up SMS Notifications',
    description: 'Configure order confirmation and shipping notification SMS messages.',
    difficulty: 'Intermediate',
    estimatedTime: '20 min',
    color: '#ef4444',
    steps: [
      {
        title: 'Get a Twilio Phone Number',
        content: 'Log into your Twilio Console. Go to **Phone Numbers > Manage > Buy a number**. Choose a number with SMS capability in your country. This is the number your notifications will come from.',
      },
      {
        title: 'Register for A2P 10DLC',
        content: 'US business messaging requires A2P 10DLC registration. Go to **Messaging > Compliance** and submit your brand registration. This typically takes 1-2 business days to approve. Without registration, your messages may be filtered.',
      },
      {
        title: 'Create a Messaging Service',
        content: 'Go to **Messaging > Services > Create Messaging Service**. Name it (e.g., "Order Notifications"). Add your phone number to the service. Enable **Sticky Sender** so customers always see the same number.',
      },
      {
        title: 'Send a Test Message',
        content: 'Use the **API Explorer** in the Twilio Console to send a test SMS. Verify the message is delivered and formatting looks correct on mobile. Check the **Monitor > Messaging Logs** for delivery status.',
      },
      {
        title: 'Add Compliance Features',
        content: 'Every SMS must include:\n- Your business name\n- An opt-out instruction: "Reply STOP to unsubscribe"\n- No prohibited content (gambling, drugs, etc.)\n\nSet up automatic STOP handling in your Messaging Service settings.',
      },
    ],
  },
  {
    id: 'vercel-deploy-guide',
    platform: 'Vercel',
    icon: '🚀',
    title: 'Deploying Your First Project',
    description: 'From GitHub repo to live website in minutes with Vercel.',
    difficulty: 'Beginner',
    estimatedTime: '10 min',
    color: '#a1a1aa',
    steps: [
      {
        title: 'Connect Your GitHub Repo',
        content: 'Go to **vercel.com** and sign up with your GitHub account. Click **New Project** and import the repository you want to deploy. Vercel auto-detects your framework (Next.js, React, Vue, etc.).',
      },
      {
        title: 'Configure Build Settings',
        content: 'Vercel usually auto-detects the right build command and output directory. For Next.js, it\'s `next build` → `.next`. For Vite/React, it\'s `vite build` → `dist`. Adjust these in **Settings > General** if needed.',
      },
      {
        title: 'Set Environment Variables',
        content: 'Go to **Settings > Environment Variables**. Add any API keys or secrets your app needs. Important: Only variables prefixed with `NEXT_PUBLIC_` are available in the browser for Next.js apps.',
      },
      {
        title: 'Deploy',
        content: 'Click **Deploy** — Vercel builds and deploys your project in about 30 seconds. You get a unique `.vercel.app` URL immediately. Every push to your main branch triggers an automatic redeploy.',
      },
      {
        title: 'Add a Custom Domain',
        content: 'Go to **Settings > Domains** and add your custom domain. Point your DNS:\n- **A Record**: @ → 76.76.21.21\n- **CNAME**: www → cname.vercel-dns.com\n\nVercel auto-provisions a free SSL certificate.',
      },
    ],
  },
  {
    id: 'shopify-discount-strategy',
    platform: 'Shopify',
    icon: '🏷️',
    title: 'Creating Effective Discount Campaigns',
    description: 'Learn to set up discount codes, automatic discounts, and track their performance.',
    difficulty: 'Beginner',
    estimatedTime: '15 min',
    color: '#22c55e',
    steps: [
      {
        title: 'Plan Your Discount Strategy',
        content: 'Before creating discounts, decide:\n- **Goal**: Clear inventory? Attract new customers? Reward loyalty?\n- **Type**: Percentage off, fixed amount, free shipping, or BOGO\n- **Duration**: Flash sale (24h), weekly, or seasonal\n- **Budget**: Calculate your margins to ensure profitability',
      },
      {
        title: 'Create a Discount Code',
        content: 'Go to **Discounts > Create discount > Discount code**. Choose a memorable code (e.g., SUMMER25, WELCOME10). Set the discount value, eligible products, minimum requirements, and expiry date.',
      },
      {
        title: 'Set Up an Automatic Discount',
        content: 'Go to **Discounts > Create discount > Automatic discount**. These apply automatically at checkout — no code needed. Great for "10% off orders over $50" or "Buy 2 get 1 free" promotions.',
      },
      {
        title: 'Promote Your Discount',
        content: 'Use Shopify\'s built-in tools:\n- **Announcement bar**: Display the discount at the top of your store\n- **Shopify Email**: Send a campaign to your subscribers\n- **Abandoned cart emails**: Include the discount to recover lost sales',
      },
      {
        title: 'Track Performance',
        content: 'Monitor results in **Analytics > Reports > Sales by discount**. Track usage count on the **Discounts** page. Compare conversion rates before and after the campaign to measure ROI.',
      },
    ],
  },
];

export default tutorialsData;
