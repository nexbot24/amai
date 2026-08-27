function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

async function registerPush(role, clientId = null) {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn('Push messaging is not supported');
        return false;
    }

    try {
        const permission = await Notification.requestPermission();
        if (permission !== 'granted') {
            console.warn('Permission for notifications was denied');
            return false;
        }

        const registration = await navigator.serviceWorker.register('/sw.js');
        await navigator.serviceWorker.ready;

        const publicVapidKey = 'BHUpB_ci9_Q9ZBbhRyguKziRcDwz3YhqxgBg7camsEoyzwOdwYlj-qlyShvLW1QU-wwMTO5MKgjifA7CxAEm76g';
        const convertedVapidKey = urlBase64ToUint8Array(publicVapidKey);

        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: convertedVapidKey
        });

        const subJson = subscription.toJSON();

        const { error } = await window.sb.from('push_subscriptions').upsert({
            role: role,
            client_id: clientId,
            endpoint: subJson.endpoint,
            keys: subJson.keys,
            created_at: new Date().toISOString()
        }, { onConflict: 'endpoint' });

        if (error) {
            console.error('Error saving subscription to Supabase:', error);
            return false;
        }

        console.log('Push notification registered successfully.');
        return true;
    } catch (error) {
        console.error('Error during push registration:', error);
        return false;
    }
}

window.registerPush = registerPush;
