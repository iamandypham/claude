# Putting the new businessgrower.io site into GHL

Written 16 Oct 2026 for OpenClaw. Andy asked for this in the Funnel Audit project: "lets launch that on the GHL", then "send it over to claw to setup on whichever funnel in GHL runs that site".

## Files
- `index.html`: the home page.
- `about.html`: the About page.
- Each file is self-contained. The CSS and JS are inline. The only external call is Google Fonts (Inter).
- Internal links already point to `/`, `/about` and `/#pricing`.

## Where the site lives (check this first)
- GHL sub-account: **BusinessGrowR** (location `F8y82aHd3V0Y4Y2ccET6`).
- Most likely funnel: **"BG Software Page"** (`hcoZ49HCpbElTBDaF36K`, path `/bg-software`). It's connected to a custom domain (domainId `s0PpJbLt8BajFQqh0YAp`). Its steps are:
  1. "Old Software Page", `/system11` (sequence 1)
  2. "New Software Page", `/system`
  3. "About", `/about`
  4. "Thank You (Clone)", `/thankyou`
- To confirm, open Settings > Domains, find businessgrower.io, and check which funnel it points at and which step serves the home page.
- Also open https://businessgrower.io in a browser and compare it with each step.
- If the domain points somewhere else, use that funnel instead. Tell Andy which one it was.

## Steps
1. **Back up first.** Clone the funnel ("BG Software Page", or whichever one serves the site) and name the copy "BG Software Page BACKUP 2026-10-16". Don't touch the clone.
2. **Home page.** Open the step that serves the businessgrower.io home page in the builder.
   - Delete the existing sections, or hide them if you want an easy rollback.
   - Add one full-width section with one row and one column.
   - Drop in a **Custom JS/HTML** element (Elements > Custom JS/HTML > Code).
   - Paste the **whole** contents of `index.html` into it. GHL keeps the `<style>` and `<script>` blocks when they sit inside the element.
   - Set the section and row padding to 0, the section width to full, and the background to none, so the page runs edge to edge.
3. **Page settings for the home step.**
   - SEO title: `BusinessGrower.io · Software`
   - SEO description: `White-labeled GoHighLevel software for trading Discord owners and educators: lead magnet pages, email, SMS, booked calls and a pipeline in one account.`
   - In Settings > Head tracking code, add:
     `<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">`
4. **About page.** Do the same on the "About" step (`/about`) with `about.html`. SEO title: `About · BusinessGrower.io`.
5. **Preview before saving live.** Use desktop and mobile preview and check each item:
   - The hero route map draws in and the "Follow one lead" board cycles.
   - The E-mail/SMS toggle switches.
   - The two price buttons open Stripe at **$1,200.00 per year** (`buy.stripe.com/eVq6oGdGm7Ei0eDfvj2VG0z`) and **$197.00 per month** (`buy.stripe.com/4gM00i8m2bUyf9x0Ap2VG0y`). Open each one and read the amount. Don't pay.
   - The Contact button, footer "Contact Us" and "Ask about Done-For-You" open the GHL contact form (`api.leadconnectorhq.com/widget/form/OJz1gQh1YDNAuiaYz1gw`).
   - The footer "Privacy Policy | Terms of Service" link opens the Google Drive legal doc.
   - The Home and About links work on the live domain.
   - Nothing scrolls sideways at phone width.
   - If GHL's own wrapper adds a white gap at the top or sides, set that section's padding and margins to 0.
6. **Save and publish** both steps. Then open https://businessgrower.io and https://businessgrower.io/about in a private window and repeat the checks in step 5.
7. **Report back** in this Slack thread:
   - which funnel and steps you changed
   - the backup clone's name
   - screenshots of desktop and mobile
   - anything that didn't render

## Don'ts
- Don't change the domain settings, the other funnels, the contact form or its consent wording, or anything on the VSL/ads funnels.
- Don't make test purchases on the Stripe links.
- Rollback: if anything looks broken after publishing, swap the backup clone's content back in, or unhide the old sections, and tell Andy.

## Head code (live since 16 Oct 2026, 8:45 PM ET)

`ghl-head-code.html` goes in Settings > Tracking Code > Header Tracking on both the Home step and the About step. It loads the Chivo font, squares the buttons, sets the motion (headline word rise, heading fade, savings bars, route lighting) and draws the account logo on any page whose header has no logo image. Replace the whole Header Tracking box with it; don't stack it on older header code.
