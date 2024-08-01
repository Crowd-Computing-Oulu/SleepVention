const serverURL = "http://127.0.0.1:8000/";
const userSpecificPages = ["mydata.html", "mystudies.html", "profile.html", "edit_profile.html"];
const MAX_STR_CARD_LENGTH = 100;
const MAX_STR_LENGTH = 2000;
const MAX_FILE_SIZE = 10 * 1024 * 1024;  // 10 MB

const own_study_image_links = [
    'https://d2jx2rerrg6sh3.cloudfront.net/images/Article_Images/ImageForArticle_22725_16560784761286902.jpg',
    'https://sjhemleymarketing.com/wp-content/uploads/2022/02/iStock-127384315411.jpg', 
    'https://www.cio.com/wp-content/uploads/2023/05/analyze_inspect_examine_find_research_data_charts_graphs_magnifying_glass_thinkstock_493572720-100724455-orig.jpeg?quality=50&strip=all',
    'https://riskonnect.com/wp-content/uploads/2022/08/attainoperationalresiliencecoverimage.jpg',
    'https://media.licdn.com/dms/image/C4E12AQE6YMoY7GKFpg/article-cover_image-shrink_720_1280/0/1520200002383?e=2147483647&v=beta&t=LSUUdpxXHBt666exiOhkdqRx_g_RDa7Y8B-UelSImnk',
    'https://e0.pxfuel.com/wallpapers/436/116/desktop-wallpaper-risk-risk-rain-risk-management.jpg'
]

const participated_study_image_links = [
    'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.fiercepharma.com%2Fpharma%2Ffda-car-t-safety-under-microscope-researchers-adverse-events-record-bcma-therapies&psig=AOvVaw2Crw9GG2i8hV8baGapIoip&ust=1722633413593000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCKDoqNfb1IcDFQAAAAAdAAAAABAU',
    'https://www.google.com/url?sa=i&url=https%3A%2F%2Fservintegrales.com.co%2F%3Fu%3Dthe-ultimate-product-research-amazon-guide-helium-10-3-hh-kDgvN0tA&psig=AOvVaw2Crw9GG2i8hV8baGapIoip&ust=1722633413593000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqGAoTCKDoqNfb1IcDFQAAAAAdAAAAABDJAQ'
]

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

function getUrlParam(urlParam) {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    return urlParams.get(urlParam);
}

function setNotificationsBadge(studyInvitations) {
    document.getElementsByClassName('badge-notification')[0].innerHTML = studyInvitations.length > 0 ? studyInvitations.length : "";
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

    if (window.location.hash === '#messages') {
        messagesContainer.style.display = 'block';
    } else {
        document.querySelector('.messages-container').style.display = 'none';
    }
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

function trimStringToMaxLength(str, maxLen) {
    return str.length > maxLen ? str.slice(0, maxLen) + '...' : str;
}

function trimJsonToMaxLength(str) {
    return str.length > (MAX_STR_LENGTH / 2) ? str.slice(0, MAX_STR_LENGTH / 2) + '\n.\n.\n.' : str;
}

function fillDataText(data) {
    content = trimStringToMaxLength(data.file_content, MAX_STR_LENGTH)
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
        <input style="max-width: 400px" class="form-control me-3" id="fileInput" type="file" accept=".txt, .json">
        <button class="btn btn-success" onclick="uploadFile()">Upload</button>
    `;
}

function reloadPage() {
    location.reload();
    alert('The information has been refreshed');
}

function generateOwnStudies(studies) {
    var studieshtml = '';
    // TODO: study_id should be in the url path not as query parameter
    studies.forEach ((study, index) => {
        description = trimStringToMaxLength(study.description, MAX_STR_CARD_LENGTH);
        studieshtml += `
            <div class="col-md-4 mt-5">
				<div class="card">
					<img src="${own_study_image_links[index]}" class="card-img-top" alt="image">
					<div class="card-body">
						<h5 class="card-title">${study.name}</h5>
						<p class="card-text">${description}</p>
						<button class="btn btn-outline-primary" onclick="window.location.href = 'study.html?studyId=${study.id}';">View</button>
					    <button class="btn btn-danger" onclick="deleteStudy(${study.id});">Remove</button>
					</div>
				</div>
			</div>
        `;
    });
    document.getElementById('studies-container').innerHTML = studieshtml;

    createStudyButton = document.getElementById('create-study-button')
    createStudyButton.innerHTML = `
        <a class="btn btn-success mt-5 mb-5" href="create_study.html">Create New Study</a>
    `;
}

function getOwnStudies() {
    var request = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        }
    };

    fetchRequest(serverURL + 'own_studies/', request)
        .then(data => {
            generateOwnStudies(data);
        })
        .catch(error => {
            handleResponseError(error);
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
            consent_form_link: document.getElementById("consent-link").value,
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

    fetchRequest(serverURL + 'study/', request)
        .then(data => {
            alert('The study has been created successfully');
            window.location.href = "mystudies.html";
        })
        .catch((response) => {
            alertError(response);
        });
}

function generateStudyHtml(study) {


    const formattedDesc = study.description.replace(/\n/g, '<br>')
    document.getElementById("study-info").innerHTML = `
        <h1>${study.name}</h1>
        <br>
        <p>${formattedDesc}</p>
        <br>
        <h5>Consent form:</h5>
        <a href="${study.consent_form_link}" target="_blank">${study.consent_form_link}</a>
        <br><br>
    `;

    document.getElementById("study-side").innerHTML = `
        <h5 class="mt-5">This study was started at:</h5>
        <div>${study.start_date}</div><br><br>
        <h5>Total number of participans:</h5>
        <div>${study.participants_number}</div><br><br>
    `;

    // If the user is the creator of the study, add the invite button and edit button to the page
    if (study.user_relation === 'creator') {
        document.getElementById("top-navbar").innerHTML = `
            <nav style="--bs-breadcrumb-divider: '>';" aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="mystudies.html">Own Studies</a></li>
                    <li class="breadcrumb-item active" aria-current="page">${study.name}</li>
                </ol>
            </nav>
        `;

        document.getElementById("study-side").innerHTML += `
            <button class="btn btn-primary mt-3" onclick="window.location.href = 'invite_user.html?studyId=${study.id}';">Invite a User</button>
        `;

        document.getElementById("study-info").innerHTML += `
            <br>
            <button id="edit-study" class="btn btn-primary mb-5">Edit Information</button>
        `;
    }

    // If the user is invited to the study, add the accept and reject button to the page
    if (study.user_relation === 'invited') {
        document.getElementById("top-navbar").innerHTML = `
            <nav style="--bs-breadcrumb-divider: '>';" aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="profile.html">Profile</a></li>
                    <li class="breadcrumb-item"><a href="profile.html#messages">Messages</a></li>
                    <li class="breadcrumb-item active" aria-current="page">${study.name}</li>
                </ol>
            </nav>
        `;

        document.getElementById("study-info").innerHTML += `
            <br>
            <input class="form-check-input" type="checkbox" value="" id="consent-checkbox" onclick="toggleAcceptButton();">
            <label class="form-check-label" for="consent-checkbox">
                I have read the consent form and agree to its conditons.
            </label>
            <br><br>
            <button class="btn btn-success mb-5 disabled" id="accept-button" onclick="acceptInvitation(${study.id});">Accept</button>
            <button class="btn btn-danger mb-5" onclick="rejectInvitation(${study.id}, 'study page');">Reject</button>
        `;
    }

    // If the user is a participant in the study, add the leave button to the page
    if (study.user_relation === 'participant') {
        document.getElementById("study-info").innerHTML += `
            <br>
            <button class="btn btn-danger mb-5">Leave</button>
        `;
    }
}

function getStudy(studyId, called_from) {
    var request = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        }
    };

    fetchRequest(serverURL + 'study/' + studyId + '/', request)
        .then(data => {
            if (called_from === 'study') {
                generateStudyHtml(data);
            } else {
                generateInviteNavbarHtml(data.id, data.name);
            }
        })
        .catch((response) => {
            handleResponseError(response);
        });
}

function deleteStudy(studyId) {
    var request = {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        }
    };
    
    fetchRequest(serverURL + 'study/' + studyId + '/', request)
        .then(data => {
            alert("The study got removed successfully");
            location.reload();
        })
        .catch((response) => {
            alertError(response);
        });
}

function submitUserInvitation() {

    emailInput = document.getElementById("email") ? document.getElementById('email').value : null;
    usernameInput = document.getElementById("username") ? document.getElementById('username').value : null;

    // Check if the input (email or username) is not empty
    if (!emailInput && !usernameInput) {
        alert("The input cannot be empty");
        return;
    }

    var request = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        },
        body: JSON.stringify({
            // "invited_by_username": isUsername,
            "email": emailInput,
            "username": usernameInput
        })
    };

    studyId = getUrlParam('studyId');
    fetchRequest(serverURL + `study/${studyId}/invite/`, request)
        .then(data => {
            alert('Invitation sent');
            // TODO: study_id should be in the url path not as query parameter
            window.location.href = `study.html?studyId=${studyId}`;
        })
        .catch(error => {
            alertError(error);
        });

}

function generateHtmlInviteUsername() {
    document.getElementById("invite-user-form").innerHTML = `
        <div class="col-auto mt-3">
            <input type="text" class="form-control" id="username" style="min-width:285px;" placeholder="Enter the user's username">
        </div>
        <div class="col-auto mt-3 mb-4">
            <button type="submit" class="btn btn-primary btn-block">Invite</button>
        </div>
        <p class="text-center">Don't have their username? <a href="#" onclick="generateHtmlInviteEmail();">Invite by email</a></p>
    `;
}

function generateHtmlInviteEmail() {
    document.getElementById("invite-user-form").innerHTML = `
        <div class="col-auto mt-3">
            <input type="text" class="form-control" id="email" style="min-width:285px;" placeholder="Enter the user's email">
        </div>
        <div class="col-auto mt-3 mb-4">
            <button type="submit" class="btn btn-primary btn-block">Invite</button>
        </div>
        <p class="text-center">Don't have their email? <a href="#" onclick="generateHtmlInviteUsername();">Invite by username</a></p>
    `;
}

function generateInviteNavbarHtml(studyId, studyName) {

    document.getElementById("top-navbar").innerHTML = `
        <nav style="--bs-breadcrumb-divider: '>';" aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="mystudies.html">Own Studies</a></li>
                <li class="breadcrumb-item" aria-current="page"><a href="study.html?studyId=${studyId}">${studyName}</a></li>
                <li class="breadcrumb-item active" aria-current="page">Invite User</li>
            </ol>
        </nav>
    `;
}

function toggleMessagesDisplay() {
    var messagesContainer = document.querySelector('.messages-container');
    if (messagesContainer) {
        if (messagesContainer.style.display === 'none') {
            messagesContainer.style.display = 'block';
        } else {
            messagesContainer.style.display = 'none';
        }
    }
}

function getMessages(calledFrom = 'default') {
    var request = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        }
    };

    fetchRequest(serverURL + 'invitations/', request)
        .then(data => {
            if (calledFrom === 'profile page') {
                generateMessagesHtml(data);
                
            } else {
                setNotificationsBadge(data);
            }
        })
        .catch(error => {
            if (calledFrom === 'profile page') {
                handleResponseError(error);
            }
        });
}

function generateMessagesHtml(studyInvitations) {
    document.getElementsByClassName('badge-messages')[0].innerHTML = studyInvitations.length > 0 ? studyInvitations.length : "";
    document.getElementsByClassName('badge-notification')[0].innerHTML = studyInvitations.length > 0 ? "..." : "";

    messagesHtml = `<ul class="list-group">`;

    studyInvitations.forEach(study => {
        studyDesc = trimStringToMaxLength(study.description, MAX_STR_CARD_LENGTH);
        messagesHtml += `
            <li class="list-group-item p-3">
                <div class="d-flex w-100 justify-content-between">
                    <h5 class="mb-3">Invited to the study:<br>"${study.name}"</h5>
                    <small class="mt-1">3 days ago</small>
                </div>
                <p class="mb-3">${studyDesc}...</p>
                <a class="btn btn-primary btn-sm" href="study.html?studyId=${study.id}">View more</a>
                <button class="btn btn-danger btn-sm" onclick="rejectInvitation(${study.id}, 'messages');">Reject</button>
            </li>
        `;
    });

    messagesHtml += '</ul>'

    document.getElementById("messages-container").innerHTML = messagesHtml;

}

function rejectInvitation(studyId, calledFrom) {
    var request = {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        }
    };
    
    fetchRequest(serverURL + 'invitation/' + studyId + '/', request)
        .then(data => {
            if (calledFrom === 'messages') {
                getMessages('profile page');
            } else {
                alert('the invitation was rejected successfully');
                window.location.href = 'profile.html#messages';
            }
        })
        .catch((response) => {
            alertError(response);
        });
}

function acceptInvitation(studyId) {
    var request = {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'token': localStorage.getItem("token")
        }
    };
    
    fetchRequest(serverURL + 'invitation/' + studyId + '/', request)
        .then(data => {
            alert('the invitation was accepted successfully');
            window.location.href = 'profile.html#messages';
        })
        .catch((response) => {
            alertError(response);
        });
}

function toggleAcceptButton() {
    document.getElementById('accept-button').classList.toggle("disabled");
}