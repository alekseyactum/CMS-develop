# actum.ua: OFF evidence and pre-DNS acceptance on the working load balancer

Project: `composite-ally-360719`. The actual pair of published paths is in
[the operational manifest](release-closed-entry-off-manifest-2026-11-20.json).
Attaching TLS did not change DNS, IAM or either existing site.

## Historical staging checkpoint (2026-11-20; not the working entry)

- Cloud Armor tier: Standard. The dedicated edge policy is `actum-ua-release-off-edge`.
  Its only rule is the enforced default `deny(403)` on `*`. No allow rule is present.
- `actum-ua-release-off-origin` and `actum-ua-release-off-deny` are empty global
  EXTERNAL_MANAGED backends with this policy, CDN disabled and request logging at 100%.
  No backend attachment or change to the deny policy is requested.
- `actum-ua-release-off-map` selects the article backend only for the two exact paths
  on the apex. Both the map and matcher default to the empty backend. Google validated
  the configuration and its seven routing examples.
- The dedicated target HTTPS proxy `actum-ua-release-off-https` references only that
  URL map and certificate map `actum-ua-release-certs`. Its sole exact-host entry
  `actum-ua-release-apex` selects `actum-ua-release-cert` for `actum.ua`. The
  certificate and exact-host entry are ACTIVE; the proxy has zero forwarding rules.
  Certificate Manager's map reported no serving targets at this checkpoint. This is a control-plane
  attachment, not a visitor-facing TLS handshake or an HTTP acceptance test.
- The current `site-front-release` origin still uses direct IAP. There is no gateway
  deployment or temporary probe. Neither a published CMS response nor a URL-map test
  is proof that a visitor can open either article via this entry.

## Certificate setup (already completed)

The operator obtained Certificate Manager access and the DNS owner added the
authorization CNAME. Retain it for automatic renewal. Do not replay the creation
steps below; they document the configuration for reference.
Check for an existing dedicated authorization/certificate/map first. Do not replace
certificates, maps, proxies or DNS for other hosts. All examples below target only
this project, global location and the apex host.

1. Create a dedicated per-project authorization and return the **actual** record:

   ```shell
   gcloud certificate-manager dns-authorizations create actum-ua-release-auth --domain=actum.ua --type=PER_PROJECT_RECORD --location=global --project=composite-ally-360719
   gcloud certificate-manager dns-authorizations describe actum-ua-release-auth --location=global --project=composite-ally-360719 --format="table(dnsResourceRecord.name,dnsResourceRecord.type,dnsResourceRecord.data)"
   ```

2. The administrator of the authoritative `srv53` zone adds **only that CNAME**.
   Verify the public name and target. Keep it for renewals. Do not switch web A/AAAA
   now. Do not change MX, TXT, NS, CAA, www or any actum.com.ua records.
3. Create a Google-managed apex certificate, an independent map and exact-host entry:

   ```shell
   gcloud certificate-manager certificates create actum-ua-release-cert --domains=actum.ua --dns-authorizations=actum-ua-release-auth --location=global --project=composite-ally-360719
   gcloud certificate-manager maps create actum-ua-release-certs --location=global --project=composite-ally-360719
   gcloud certificate-manager maps entries create actum-ua-release-apex --map=actum-ua-release-certs --certificates=actum-ua-release-cert --hostname=actum.ua --location=global --project=composite-ally-360719
   gcloud certificate-manager certificates describe actum-ua-release-cert --location=global --project=composite-ally-360719 --format="value(managed.state)"
   ```

   Check the certificate/map resource names and ACTIVE certificate status. The map
   belongs **only to the dedicated HTTPS proxy**, not the existing site's proxy.
   [Google's DNS authorization guide](https://docs.cloud.google.com/certificate-manager/docs/domain-authorization).

## Pre-DNS acceptance on the production serving path (decision 2026-11-21)

Do not build a pilot gateway or create a temporary VM. The staging inventory above is
historical: it is not a deployment recipe or proof that the working entry serves traffic.

**Origin evidence, 2026-11-21.** Google-authenticated document GETs to the release site's
run.app URL returned 200 for both manifest routes. HTML lang was uk/ru respectively and
each H1 matched its manifest hash. Chrome showed the same response header on both documents:
`Cache-Control: private, no-cache, no-store, max-age=0, must-revalidate`.
No CMS response, Google login page or Next prefetch was counted. This is not LB evidence.

**Next gate, not yet run:**

1. Before switching public DNS, identify the actual production HTTPS frontend address(es),
   forwarding rule, certificate and intended site backend for actum.ua. Use the path that
   will receive real traffic, not a temporary backend. Both CDN and Next cache must be OFF.
   Use an existing authorized client and the intended access policy. If the path or access
   is not ready, stop; do not remove IAP, grant access, or provision a test gateway/VM.
2. For each of the two exact manifest paths, route just the test client's request to the
   working LB address while keeping the real HTTPS URL, Host and TLS SNI. For example:
   `curl --resolve "actum.ua:443:<working-LB-IP>" -D - "https://actum.ua<manifest-path>"`.
   This is a GET, not HEAD. Do not use `-k`, follow redirects, add cache-busting parameters
   or substitute the run.app domain. Do not retain cookies or authentication headers in evidence.
3. Require valid TLS for actum.ua, HTTP 200 text/html, the correct lang and H1 for each
   article and the no-store response directive. Correlate the requests with the working LB's
   logs (host, path, time, selected frontend/backend). A CMS/API response, an IAP redirect,
   a parking page or a validated URL map does not pass. Verify the existing access policy;
   do not create a new IP allowlist for this test.
4. On failure or missing evidence: keep DNS unchanged and both caches OFF. On success:
   record sanitized evidence and request separate approval for the apex web A/AAAA cutover
   (including IPv6 routing if published). Repeat both GETs via ordinary DNS after cutover.
   Leave actum.com.ua, www, mail and the certificate authorization CNAME untouched.
5. Only in a separately approved cache pilot verify a real CDN HIT, fresh HTML after a
   published change and a same-host rollback to OFF on the working path. The pre-DNS
   no-store test does not prove any of those. No infrastructure change is authorized here.
