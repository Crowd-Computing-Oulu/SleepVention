const serverURL = "http://127.0.0.1:8000/"

async function fetchRequest(url, request) {
    const response = await fetch(url, request);
    if (response.ok) {
        return response.json();
    }
    return Promise.reject(response);
}

function alertError(response) {
    response.json().then(data => {
        alert("Error " + response.status + ": " + data.detail);
    })
}

function handleResponseError(error) {
    if (error.status === 401) {
        // Handle unathorized error
        window.location.href = "login.html";
    } else {
        alertError(error);
    }
}

function submitRegister() {
    var username = document.getElementById("username").value;
    var email = document.getElementById("email").value;
    var password = document.getElementById("password").value;

    var request = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            "username": username,
            "email": email,
            "password": password
        })
    };

    fetchRequest(serverURL + 'register/', request)
        .then(data => {
            localStorage.setItem("token", data.token);
            window.location.href = "profile.html";
        })
        .catch(error => {
            alertError(error);
        });

}

function submitLogin() {
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    var request = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            "username": username,
            "password": password
        })
    };

    fetchRequest(serverURL + 'login/', request)
        .then(data => {
            localStorage.setItem("token", data.token);
            window.location.href = "homepage.html";
        })
        .catch(error => {
            alertError(error);
        });

}

function generateProfileHtml(profileInfo) {
    // Get the info div element
    var infoDiv = document.getElementById("profileInfo");

    infoDiv.innerHTML = `
        <h5 class="card-title mt-4 mb-3">${profileInfo.username}</h5>
        <p class="card-text">Email: ${profileInfo.email}</p>
        <p class="card-text">Nationality: ${profileInfo.nationality}</p>
        <p class="card-text">Date of birth: ${profileInfo.birth_date}</p>
        <p class="card-text">Gender: ${profileInfo.gender}</p>
        <p class="card-text">Height: ${profileInfo.height}</p>
        <p class="card-text">Weight: ${profileInfo.weight}</p>
    `;

    // localStorage.setItem("username", restaurantInfo.id);
}


function getProfile(page) {
    // TODO: get restaurant information from server

    var request = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        }
    };

    fetchRequest(serverURL + 'profile/', request)
        .then(data => {
            if (page === "profile page") {
                generateProfileHtml(data);
            } else {
                fillForm(data);
            }
        })
        .catch(error => {
            handleResponseError(error);
        });
}

function fillForm(profileInfo) {
    // document.getElementById("username").value = profileInfo.username;
    // document.getElementById("email").value = profileInfo.email;
    document.getElementById("nationality").value = profileInfo.nationality;
    document.getElementById("birthdate").value = profileInfo.birth_date;
    document.getElementById("gender").value = profileInfo.gender;
    document.getElementById("height").value = profileInfo.height;
    document.getElementById("weight").value = profileInfo.weight;
}

function getProfileEditForm() {

    const profileForm = Object.fromEntries(
        Object.entries({
            nationality: document.getElementById("nationality").value,
            birth_date: document.getElementById("birthdate").value,
            gender: document.getElementById("gender").value,
            height: document.getElementById("height").value,
            weight: document.getElementById("weight").value,
        }).filter(([key, value]) => value !== "")
    );

    return profileForm;
}

function submitProfile() {
    const updatedProfile = getProfileEditForm();

    var request = {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        },
        body: JSON.stringify(updatedProfile)
    };

    fetchRequest(serverURL + 'profile/', request)
        .then(data => {
            alert('The information submitted.');
            window.location.href = "profile.html";
        })
        .catch((response) => {
            alertError(response);
        });
}

function reconfigureNavbar() {
    var mydataNavItem = document.getElementById("navbar-data");
    var mystudiesNavItem = document.getElementById("navbar-studies");
    var profileNavItem = document.getElementById("navbar-profile");

    mydataNavItem.style.display = "none";
    mystudiesNavItem.style.display = "none";
    profileNavItem.style.display = "none";

    var loginNavItem = document.getElementById("navbar-login");
    loginNavItem.innerHTML = '<a class="nav-link" href="login.html">Log In</a>';
}

function getHomepage() {

    var request = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        }
    };

    fetchRequest(serverURL + 'home/', request)
        .then(data => {
            if (data === "Not authorized") {
                reconfigureNavbar();
            }
        })
        .catch(error => {
            alertError(error);
        });
}

function getExplore() {

    var request = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        }
    };

    fetchRequest(serverURL + 'explore/', request)
        .then(data => {
            if (data === "Not authorized") {
                reconfigureNavbar();
            }
        })
        .catch(error => {
            alertError(error);
        });
}

function getAboutUs() {

    var request = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        }
    };

    fetchRequest(serverURL + 'about-us/', request)
        .then(data => {
            if (data === "Not authorized") {
                reconfigureNavbar();
            }
        })
        .catch(error => {
            alertError(error);
        });
}