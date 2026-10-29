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
  for (var k in fields) { if (fields.hasOwnProperty(k) && fields[k] && k !== 'botcheck') lines.push(k + ': ' + fields[k]); }
  var bodyText = lines.join('\n');

  function mailto() {
    window.location.href = 'mailto:sales@datacore.com.sa?subject=' +
      encodeURIComponent(subject) + '&body=' + encodeURIComponent(bodyText);
    return 'mail';
  }

  if (!window.DCP_FORM_KEY) { return Promise.resolve(mailto()); }

  var payload = {};
  for (var f in fields) { if (fields.hasOwnProperty(f)) payload[f] = fields[f]; }
  // set after the form fields, so a field with one of these names cannot replace them
  payload.access_key = window.DCP_FORM_KEY;
  payload.subject = subject;
  payload.from_name = 'Datacore website';   // the visitor's name stays in the message as an ordinary field
  payload.botcheck = fields.botcheck || '';   // a hidden field people leave empty; Web3Forms drops the message when it is filled

  return fetch('https://api.web3forms.com/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify(payload)
  }).then(function (r) {
    if (!r.ok) return mailto();
    // Web3Forms can answer 200 with success: false; only success: true counts as delivered
    return r.json().then(function (j) { return j && j.success === true ? 'sent' : mailto(); },
                         function () { return mailto(); });
  }).catch(function () { return mailto(); });
};
