// Generate a random string (code_verifier)
function generateCodeVerifier() {
    const array = new Uint8Array(32);
    window.crypto.getRandomValues(array);
    return btoa(String.fromCharCode.apply(null, array))
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=/g, "");
}

// Convert code_verifier to a hashed code_challenge
async function generateCodeChallenge(codeVerifier) {
    const encoder = new TextEncoder();
    const data = encoder.encode(codeVerifier);
    const hashBuffer = await window.crypto.subtle.digest("SHA-256", data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return btoa(String.fromCharCode.apply(null, hashArray))
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=/g, "");
}

// Step 1: Generate PKCE parameters and redirect the user
export async function redirectToFitbitAuth() {
    const clientId = "23Q77F";
    const redirectUri = "http://127.0.0.1:8000/fitbit-authenticate";
    const scopes = "activity cardio_fitness electrocardiogram heartrate location nutrition oxygen_saturation profile respiratory_rate settings sleep social temperature weight"; // Add other scopes if needed

    // Generate PKCE parameters
    const codeVerifier = generateCodeVerifier();
    const codeChallenge = await generateCodeChallenge(codeVerifier);

    // Save the code_verifier in sessionStorage for later use (when exchanging for an access token)
    sessionStorage.setItem("code_verifier", codeVerifier);

    // Construct Fitbit authorization URL
    const authUrl = `https://www.fitbit.com/oauth2/authorize?`
        + `response_type=code`
        + `&client_id=${clientId}`
        + `&redirect_uri=${encodeURIComponent(redirectUri)}`
        + `&scope=${encodeURIComponent(scopes)}`
        + `&code_challenge=${codeChallenge}`
        + `&code_challenge_method=S256`;

    // Step 2: Open a new tab and redirect the user to Fitbit login
    window.open(authUrl, "_blank").focus();
}
