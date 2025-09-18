function format_datetime(datetime) {
    "use strict";
    const event = new Date(datetime);
    return event.toLocaleString('en-US')
}

function format_datetime_detailed(datetime) {
    "use strict";
    const event = new Date(datetime);
    return event.toString()
}
