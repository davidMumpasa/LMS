function sendStatement(verb, verbId,object,objectId) {
    const player = GetPlayer();
    const uNameJs = player.GetVar("uName");
    const uEmailJs = player.GetVar("uEmail");

    const conf = {
        "endpoint": "https://lms.lrs.io/xapi/",
        "auth": "Basic " + toBase64("kaunee:ifahat")
    }
    ADL.XAPIWrapper.changeCongig(conf);
    const statement = {

        "actor": {
            "mbox": "mailto:" + uNameJs,
            "name": uEmailJs
        },
        "verb": {
            "id": verbId,
            "display": {
                "en-US": verb
            }
        },
        "object": {
            "id": objectId,
            "definition": {
                "name": {
                    "en-US": object
                }
            }
        }
    }
    const result = ADL.XAPIWrapper.sendStatement(statement);
}


