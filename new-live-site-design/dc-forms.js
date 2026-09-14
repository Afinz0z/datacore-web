/* Datacore — form delivery. Best-effort, with NO silent drops.
 *
 * Two paths:
 *   1. If DCP_FORM_KEY is set below (a free Web3Forms access key tied to your
 *      inbox), submissions POST straight through to that inbox — the visitor
 *      needs no email client. Get a key in ~30s at https://web3forms.com by
 *      entering sales@datacore.com.sa; paste the key into DCP_FORM_KEY.
 *   2. Otherwise — or if that POST ever fails — the visitor's own email app
 *      opens pre-filled to sales@datacore.com.sa with their details, so a
 *      request is never lost the way the old demo lost it.
 *
 * dcpDeliver(fields, subject) returns a Promise that resolves to:
 *   'sent'  — POSTed to the inbox (seamless), or
 *   'mail'  — the visitor's email app was opened pre-filled.
 */
window.DCP_FORM_KEY = window.DCP_FORM_KEY || '1519203c-5bbc-47fe-8d33-681ab3e29622';   /* Web3Forms access key -> sales@datacore.com.sa */

window.dcpDeliver = function (fields, subject) {
  var lines = [];
  for (var k in fields) { if (fields.hasOwnProperty(k) && fields[k]) lines.push(k + ': ' + fields[k]); }
  var bodyText = lines.join('\n');

  function mailto() {
    window.location.href = 'mailto:sales@datacore.com.sa?subject=' +
      encodeURIComponent(subject) + '&body=' + encodeURIComponent(bodyText);
    return 'mail';
  }

  if (!window.DCP_FORM_KEY) { return Promise.resolve(mailto()); }

  var payload = { access_key: window.DCP_FORM_KEY, subject: subject,
                  from_name: fields.name || fields.Name || 'Datacore website' };
  for (var f in fields) { if (fields.hasOwnProperty(f)) payload[f] = fields[f]; }

  return fetch('https://api.web3forms.com/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify(payload)
  }).then(function (r) { return r.ok ? 'sent' : mailto(); })
    .catch(function () { return mailto(); });
};
