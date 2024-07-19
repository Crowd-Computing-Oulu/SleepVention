const serverURL = "http://127.0.0.1:8000/";
const userSpecificPages = ["mydata.html", "mystudies.html", "profile.html", "edit_profile.html"];
const MAX_STR_LENGTH = 2000;
const MAX_FILE_SIZE = 10 * 1024 * 1024;  // 10 MB

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

function verifyRegisterInfor(username, email, password) {
    // Check if username is more than 3 characters
    if (username.length <= 3) {
        alert("Username must be more than 3 characters long.");
        return false;
    }

    // Regular expression for validating email
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert("Invalid email format.");
        return false;
    }

    // Regular expression for validating password
    var passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;
    if (!passwordRegex.test(password)) {
        alert("Password must be at least 8 characters long and include a combination of lowercase and uppercase letters and numbers.");
        return false;
    }

    return true;
}

function submitRegister() {
    var username = document.getElementById("username").value;
    var email = document.getElementById("email").value;
    var password = document.getElementById("password").value;

    if (!verifyRegisterInfor(username, email, password)) {
        return;
    }

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

function getCurrentPage() {
    var currentPath = window.location.pathname;
    var currentPage = currentPath.substring(currentPath.lastIndexOf('/') + 1);
    return currentPage;
}

function logOut() {
    localStorage.setItem("token", "-");

    alert("Loging out was successful");
    
    const currentPage = getCurrentPage();
    if (userSpecificPages.includes(currentPage)) {
        window.location.href = "homepage.html";
    } else {
        window.location.reload();
    }
}

function fillDataTable(data) {
    var tableHtml = `
		<table class="table table-hover w-50" id="data-table">
        <thead><tr>
    `;
    for (var column_name in data[0]) {
        tableHtml += `<th>${column_name}</th>`;
    }
    tableHtml += `</tr></thead><tbody>`;

    data.forEach(dataRow => {
        tableHtml += `<tr>`;
        for (var column_name in dataRow) {
            tableHtml += `<td>${dataRow[column_name]}</td>`;
        }
        tableHtml += `</tr>`;
    });
    tableHtml += `</tbody></table>`;

    document.getElementById('data-content').innerHTML = tableHtml;
}

function fillDataTableVertically(data) {
    var tableHtml = `
		<table class="table table-hover w-50" id="data-table">
        <thead>
            <tr>
                <th>Parameter Name</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
    `;

    data.forEach(dataRow => {
        for (var column_name in dataRow) {
            tableHtml += `
                <tr>
                    <td>${column_name}</td>
                    <td>${dataRow[column_name]}</td>
                </tr>
            `;
        }
    });
    tableHtml += `</tbody></table>`;

    document.getElementById('data-content').innerHTML = tableHtml;
}

function trimStringToMaxLength(str) {
    return str.length > MAX_STR_LENGTH ? str.slice(0, MAX_STR_LENGTH) + '...' : str;
}

function trimJsonToMaxLength(str) {
    return str.length > (MAX_STR_LENGTH / 2) ? str.slice(0, MAX_STR_LENGTH / 2) + '\n.\n.\n.' : str;
}

function fillDataText(data) {
    content = trimStringToMaxLength(data.file_content)
    document.getElementById('data-content').innerHTML = `
        <p style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; width: 80%;">
            ${content}
        </p>
    `;
}

function fillDataJson(data) {
    content = JSON.stringify(JSON.parse(data.file_content), null, 4);
    document.getElementById('data-content').innerHTML = `
        <pre id="json-content" style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; width: 80%;"><code>
        </code></pre>
    `;
    document.getElementById('json-content').innerText = trimJsonToMaxLength(content);
}

function generateDataDateButtons(dataLog, data_category) {
    for (var data_date in dataLog) {
        document.getElementById(`${data_category}-date-buttons`).innerHTML += `
            <li class="mb-1">
                <li><a href="#" class="link-dark d-inline-flex text-decoration-none rounded ${data_category}-date-button" data-date="${data_date}">${data_date}</a></li>
            </li>
        `;
    }

    
    var dataDateButtons = document.querySelectorAll(`.${data_category}-date-button`);
    dataDateButtons.forEach(button => {
        button.addEventListener('click', function() {
            var dataDate = button.dataset.date;

            if (data_category === "sleep") {
                fillDataTableVertically(dataLog[dataDate]);
            } else {
                fillDataTable(dataLog[dataDate]);
            }
        });
    });
}

function generateFilesButtons(dataFiles) {
    dataFiles.forEach((dataFile, index) => {
        document.getElementById('files-buttons').innerHTML += `
            <li class="mb-1">
                <li><a href="#" class="link-dark d-inline-flex text-decoration-none rounded file-name-button" data-file-button-id="${index}">${dataFile.file_name}</a></li>
            </li>
        `;
    });


    var dataFileButtons = document.querySelectorAll('.file-name-button');
    dataFileButtons.forEach(button => {
        button.addEventListener('click', function() {
            var dataFileId = button.dataset.fileButtonId;
            if (dataFiles[dataFileId].file_name.endsWith(".json")) {
                fillDataJson(dataFiles[dataFileId]);
            } else {
                fillDataText(dataFiles[dataFileId]);
            }
        });
    });
}

function fillMyDataPage(data) {
    generateDataDateButtons(data.activities, 'activity');
    generateDataDateButtons(data.heartrate, 'hr');
    generateDataDateButtons(data.sleep, 'sleep');
    generateDataDateButtons(data.sleep_levels, 'levels');
    generateFilesButtons(data.files)
}

function getMyData() {
    var request = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        }
    };

    fetchRequest(serverURL + 'mydata/', request)
        .then(data => {
            fillMyDataPage(data);
        })
        .catch(error => {
            if (error.status === 403) {
			    window.open("https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23PDRW&scope=activity+cardio_fitness+electrocardiogram+heartrate+location+nutrition+oxygen_saturation+profile+respiratory_rate+settings+sleep+social+temperature+weight&code_challenge=lMNXGvUcuN9QrksqDqnUpS4YaUhIWzaTNH3KJEpV_jA&code_challenge_method=S256&state=" + localStorage.getItem("token"), '_blank').focus();
            }
            else {
                handleResponseError(error);
            }
        });
}

function uploadFile() {
    const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];

            if (file) {
                if (file.size > MAX_FILE_SIZE) {
                    alert('File size exceeds 10 MB. Please choose a smaller file.');
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(e) {
                    const file_content = e.target.result;

                    request = {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'token': localStorage.getItem("token")
                        },
                        body: JSON.stringify({ file_name: file.name, file_content: file_content })
                    }

                    fetchRequest(serverURL + 'data_file/', request)
                        .then(data => {
                            alert('File uploaded successfully');
                        })
                        .catch(error => {
                            alertError(error);
                        });
                };
                reader.readAsText(file);
            } else {
                alert('Please select a file');
            }
}

function generateUploadButton() {
    document.getElementById("data-content").innerHTML = `
        <input style="max-width: 400px" class="form-control form-control me-3" id="fileInput" type="file" accept=".txt, .json">
        <button class="btn btn-success" onclick="uploadFile()">Upload</button>
    `;
}

function reloadPage() {
    location.reload();
    alert('The information has been refreshed');
}

function getOwnStudies() {
    var studieshtml = '';
    for (let i = 0; i < 1; i++) {
        studieshtml += `
            <div class="col-md-4 mt-5">
				<div class="card">
					<img src="https://www.hypersomniafoundation.org/wp-content/uploads/2024/01/iStock-1358653596-brain-waves-1024x784.jpg" class="card-img-top" alt="image">
					<div class="card-body">
						<h5 class="card-title">Effects of Various Activities on Sleep</h5>
						<p class="card-text">The description of the study comes here...</p>
						<button class="btn btn-outline-primary"">View</button>
					<button class=" btn btn-danger"">Remove</button>
					</div>
				</div>
			</div>
            <div class="col-md-4 mt-5">
				<div class="card">
					<img src="https://amerisleep.com/blog/wp-content/uploads/2020/01/What_is_a_Sleep_Study_and_How_Does_it_Work-01-scaled.jpg" class="card-img-top" alt="image">
					<div class="card-body">
						<h5 class="card-title">Diagnosing Daytime Multiple Sleep Latency Test</h5>
						<p class="card-text">The description of the study comes here...</p>
						<button class="btn btn-outline-primary"">View</button>
					<button class=" btn btn-danger"">Remove</button>
					</div>
				</div>
			</div>
        `;
    }
    document.getElementById('studies-container').innerHTML = studieshtml;

    createStudyButton = document.getElementById('create-study-button')
    createStudyButton.innerHTML = `
        <button class="btn btn-success mt-4 mb-5">Create New Study</button>
    `;
    createStudyButton.addEventListener('click', function() {
        window.location.href = 'create_study.html';
    });
}

function getParticipatedStudies() {
    var studieshtml = `
            <div class="col-md-4 mt-5">
				<div class="card">
					<img src="https://www.mecfs.de/wp-content/uploads/2022/06/Research-Foundation-Header.jpg" class="card-img-top" alt="image">
					<div class="card-body">
						<h5 class="card-title">Sleep Research into ME/CFS</h5>
						<p class="card-text">The description comes here...</p>
						<button class="btn btn-outline-primary"">View</button>
					<button class=" btn btn-danger"">Leave</button>
					</div>
				</div>
			</div>
            <div class="col-md-4 mt-5">
				<div class="card">
					<img src="https://www.bruker.com/en/landingpages/bbio/mr-for-battery-research/battery-research-probes-li-ion-technologies/_jcr_content/teaserImage.coreimg.jpeg/1697635985708/adobestock-605065614.jpeg" class="card-img-top" alt="image">
					<div class="card-body">
						<h5 class="card-title">Sleep Research for Energy</h5>
						<p class="card-text">The description comes here...</p>
						<button class="btn btn-outline-primary"">View</button>
					<button class=" btn btn-danger"">Leave</button>
					</div>
				</div>
			</div>
            <div class="col-md-4 mt-5">
				<div class="card">
					<img src="https://brainvision.com/wp-content/uploads/2020/05/Brain-Vision-EEG-Sleep-Research-wText.png" class="card-img-top" alt="image">
					<div class="card-body">
						<h5 class="card-title">EEG Sleep Research</h5>
						<p class="card-text">The description comes here...</p>
						<button class="btn btn-outline-primary"">View</button>
					<button class=" btn btn-danger"">Leave</button>
					</div>
				</div>
			</div>
        `;

    document.getElementById('studies-container').innerHTML = studieshtml;

    document.getElementById('create-study-button').innerHTML = '';
}

function goToOwnStudies() {
    const navButtons = document.querySelectorAll('#studies-nav .nav-item button');
    navButtons[0].className = 'inside-nav nav-link active';
    navButtons[1].className = 'inside-nav nav-link';
    getOwnStudies();
}

function goToParticipatedStudies() {
    const navButtons = document.querySelectorAll('#studies-nav .nav-item button');
    navButtons[0].className = 'inside-nav nav-link';
    navButtons[1].className = 'inside-nav nav-link active';
    getParticipatedStudies();
}

function submitEdittedDataPrivacy(editingCategory) {
    var request = {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        },
        body: JSON.stringify({
            "data_category": editingCategory
        })
    };

    fetchRequest(serverURL + 'data_privacy/', request)
        .then(data => {
            getDataSettings();
        })
        .catch((response) => {
            alertError(response);
        });
}

function generateDataSettings(data) {
    dataHTML = `
        <table class="table table-striped w-50">
				<thead>
					<tr>
						<th>Data</th>
						<th>Public</th>
					</tr>
				</thead>
				<tbody>
    `;

    for (var dataCategory in data) {
        dataHTML += `
            <tr>
                <td>${dataCategory}</td>
                <td>
                    <span class="form-switch">
                        <input class="form-check-input data-public-switch" type="checkbox" role="switch" data-category="${dataCategory}">
                    </span>
                </td>
            </tr>
        `;
    }

    dataHTML += `</tbody></table>`

    document.getElementById('data-content').innerHTML = dataHTML;

    var switchButtons = document.querySelectorAll('.data-public-switch');
    switchButtons.forEach(button => {
        button.checked = data[button.dataset.category];

        button.addEventListener('click', function() {
            var EditedDataCategory = button.dataset.category;
            submitEdittedDataPrivacy(EditedDataCategory);
        });
    });
}

function getDataSettings() {
    var request = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        }
    };

    fetchRequest(serverURL + 'data_privacy/', request)
        .then(data => {
            generateDataSettings(data);
        })
        .catch(error => {
            handleResponseError(error);
        });
}

function getCreateStudyForm() {
    const studyForm = Object.fromEntries(
        Object.entries({
            name: document.getElementById("name").value,
            description: document.getElementById("description").value,
            type: document.getElementById("type").value,
            consent_link: document.getElementById("consent-link").value,
        })
    );

    return studyForm;
}

function submitNewStudy() {
    const studyForm = getCreateStudyForm();

    var request = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        },
        body: JSON.stringify(studyForm)
    };

    fetchRequest(serverURL + 'create_study/', request)
        .then(data => {
            alert('The study has been created successfully');
            window.location.href = "mystudies.html";
        })
        .catch((response) => {
            alertError(response);
        });
}