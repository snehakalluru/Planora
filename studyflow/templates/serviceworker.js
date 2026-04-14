self.addEventListener("push", function(event) {
    const payload = event.data ? event.data.json() : {};
    const title = payload.title || "StudyFlow Reminder";
    const options = {
        body: payload.body || "You have a task reminder waiting.",
        data: {
            url: payload.url || "/tasks/",
        },
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", function(event) {
    event.notification.close();
    const destination = event.notification.data && event.notification.data.url
        ? event.notification.data.url
        : "/tasks/";

    event.waitUntil(clients.openWindow("{{ site_origin }}" + destination));
});
