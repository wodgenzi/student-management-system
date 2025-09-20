function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function hideOptions(dropdown) {
    const wrapper = dropdown.querySelector('.inpt-wrapper');
    const main = dropdown.querySelector('.main-selected');
    const options = dropdown.querySelector('.drpdwn-optns');
    options.style.display = 'none';
    main.classList.add('disabled');
    main.style.pointerEvents = 'none';
    wrapper.classList.remove('active');
}
function initDropdowns() {
    const dropdowns = document.querySelectorAll('.drpdwn');

    dropdowns.forEach((dropdown) => {
        if (dropdown.dataset.dropdownInit === "true") return;
        const wrapper = dropdown.querySelector('.inpt-wrapper');
        const main = dropdown.querySelector('.main-selected');
        const options = dropdown.querySelector('.drpdwn-optns');
        let items = options.querySelectorAll('li');

        function toggleOptions() {
            if (options.style.display === 'none'){
                options.style.display = 'block';
                wrapper.classList.add('active')
                if (dropdown.classList.contains('reset')) {main.value = "";}
            }
            else {options.style.display = 'none';wrapper.classList.remove('active')}
        }



        wrapper.addEventListener('click', toggleOptions);

        if (dropdown.classList.contains('flexible')) {
            wrapper.addEventListener('click', () => {
                main.style.pointerEvents = 'auto';
                main.classList.remove('disabled');
                main.focus()
            });
        }
        if (dropdown.classList.contains('searchable')) {
            items = Array.from(items).slice(1);
            const searchBox = document.getElementById('optns-srch');
            searchBox.addEventListener('input', () => {
                const searchText = searchBox.value.toLowerCase();
                items.forEach(item => {
                    const option = item.textContent.toLowerCase()
                    item.style.display = option.includes(searchText) ? 'block' : 'none';
               });
            });
        }

        items.forEach(item => {
           item.addEventListener('click', () => {
               main.dataset.value = item.dataset.value;
               main.value = item.dataset.value;
               dropdown.classList.contains('shut') && hideOptions(dropdown);
           });
        });
        dropdown.dataset.dropdownInit = "true";
    });
}

async function add_data(url, name, path = null) {
    const response = await fetch(url);
    const html = await response.text();

    setupModal(`${name}-modal-container`, `${name}-modal-content`, html);
    styleFormElements('.modal-container');
    setupForm(url, name, path);

}

async function showNotification(text, type = "info", duration = 2000) {
    const notif = document.getElementById('notification-container');
    notif.textContent = text;
    notif.style.top = '115px';
    await sleep(duration)
    notif.style.top = '60px';
}

function setupModal(containerId, contentId, html, closeButtonId = null) {
    const closeId = closeButtonId || `close-${containerId.split('-')[0]}-modal`;
    document.getElementById(contentId).innerHTML =
        `<button id="${closeId}" class="button-02" type="button" style="position:absolute; top:10px; right:10px;">&times;</button>` + html;
    document.getElementById(containerId).style.display = 'block';
    document.getElementById(closeId).onclick = function () {
        document.getElementById(containerId).style.display = 'none';
    };

    switch (contentId) {
        case 'student-modal-content':
            document.getElementById('id_contact').placeholder = 'N/A';
            break;
        case 'enrollment-modal-content':
            addEnrollmentButtons('enrollment');
            break;
    }

}

// Style form elements
function styleFormElements(formSelector) {
    document.querySelectorAll(`${formSelector} form p`).forEach(p => {
        p.style.display = 'flex';
        p.style.alignItems = 'center';

        const input = p.querySelector("input");
        if (input) input.classList.add('editable', 'default-input', 'form-input');

        const select = p.querySelector("select");
        if (select) select.classList.add('editable', 'default-dropdown', 'form-select');
    });
}


// Add "Add Student" button
function addEnrollmentButtons(path) {
    const studentSelect = document.getElementById('add-student-dropdown');
    const timingSelect = document.getElementById('id_timing');
    if (studentSelect && !studentSelect.parentNode.querySelector('.button-02')) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.classList.add('button-02');
        btn.textContent = 'Add Student';
        btn.style.marginLeft = '8px';
        btn.style.padding = '0';
        btn.onclick = () => add_data('/admissions/add-student/', 'student', path);
        studentSelect.parentNode.insertBefore(btn, studentSelect.nextSibling);
    }
    if (timingSelect && !timingSelect.parentNode.querySelector('.button-02')) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.classList.add('button-02');
        btn.textContent = 'Add Timing';
        btn.id = 'add-time-btn';
        btn.style.marginLeft = '8px';
        timingSelect.parentNode.insertBefore(btn, timingSelect.nextSibling);

        const inpt = document.createElement('input')
        inpt.type = 'time';
        inpt.id = 'new-time-input';
        inpt.style.display = 'none';
        timingSelect.parentNode.insertBefore(inpt, timingSelect.nextSibling);

    }
    setupEnrollmentButtons()


}

function setupEnrollmentButtons() {
    document.getElementById('add-time-btn').onclick = function () {
        document.getElementById('new-time-input').style.display = 'inline';
        document.getElementById('id_timing').style.display = 'none';
        document.getElementById('new-time-input').focus();
    };
    document.getElementById('new-time-input').onchange = function () {
        const select = document.getElementById('id_timing');
        const newOption = document.createElement('option');
        newOption.value = this.value;
        newOption.text = this.value;
        select.add(newOption);
        select.value = this.value;
    };
}

// Handle form submission
async function handleFormSubmission(form, url, onSuccess, onError) {
    const formData = new FormData(form);
    const options = {
        method: 'POST',
        body: formData
    };

    if (url.includes('add-student') || url.includes('add-enrollment')) {
        options.headers = {'X-Requested-With': 'XMLHttpRequest'};
    }

    const response = await fetch(url, options);
    const html = await response.text();

    if (response.ok && !html.includes('errorlist')) {
        onSuccess();
    } else {
        onError(html);
    }
}


async function refreshForm(url, name) {
    const response = await fetch(url);
    const html = await response.text();

    setupModal(`${name}-modal-container`, `${name}-modal-content`, html);
    styleFormElements('.modal-container');
    if (name === 'enrollment') {
        addEnrollmentButtons(name);
    }

    setupForm(url, name);
}

function setupForm(url, name, path) {
    const form = document.querySelector(`#${name}-modal-content form`);
    if (form) {
        form.onsubmit = async function (e) {
            e.preventDefault();
            await handleFormSubmission(
                form,
                url,
                () => {
                    document.getElementById(`${name}-modal-container`).style.display = 'none';
                    if (path) {
                        refreshForm(`/admissions/add-${path}/`, path);
                    } else {
                        updateTable(name)
                    }
                },
                (html) => {
                    setupModal(`${name}-modal-container`, `${name}-modal-content`, html);
                    setupForm(url, name);
                }
            );
        };
        initDropdowns();
    }
}

async function add_to_contacts(button) {
    const row = button.closest('tr');
    const cell = button.closest('td');
    if (cell.querySelector('.loader')) {
        return; // Prevent multiple clicks
    }
    const loader = document.createElement('div');
    loader.className = 'loader';
    cell.appendChild(loader);
    cell.removeChild(button);
    const response = await fetch('add-contact/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'name': row.dataset.name,
            'phone': row.dataset.phone,
            'phone_type': 'Personal',
            'relation_type': 'Father',
            'relation_value': row.dataset.father_name,
        })
    });
    const result = await response.json();
    if (result.exists){
        showNotification("Contact Already Exists!")
    } else {
        showNotification("Added to Contacts!")
    }
    cell.removeChild(loader);
    cell.appendChild(button);

}

function toggleDetails(btn) {
    const row = btn.closest('tr');
    const next = row.nextElementSibling;
    if (next && next.classList.contains('details')) {
        next.style.display = next.style.display === 'none' ? 'table-row' : 'none';
    }
}

function toggleDisplay(element) {
    element.style.display = element.style.display === 'none' ? 'block' : 'none';
}

function updateTable(name, order = null) {
    let url = `/admissions/${name}s/`;
    if (order) {
        url += `?order=${order}`;
    }
    htmx.ajax('GET', url, {
        target: '#main-sc-contents',
        swap: 'innerHTML'
    });
}

let sortVar = '-id';

function sortTable(name, header, order = null) {
    if (sortVar === order) {
        if (sortVar.startsWith("-")) {
            order = order.replace("-", "");
        } else {
            order = `-${order}`;
        }
    }

    let url = `/admissions/${name}s/`;
    if (order) {
        url += `?order=${order}`;
    }
    htmx.ajax('GET', url, {
        target: '#main-sc-contents',
        swap: 'innerHTML'
    });
    sortVar = order;
}

async function addFilter(start_date, end_date, selectedStatuses) {
    let update_url = '/accounts/update-profile-settings/';
    let data = {
        'start_date': start_date,
        'end_date': end_date,
        'statuses': selectedStatuses.join(",")
    };
    await fetch(update_url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })

    let url = `/admissions/enrollments/`;
    htmx.ajax('GET', url, {
        target: '#main-sc-contents',
        swap: 'innerHTML'
    });
}

const mediaQuery = window.matchMedia("(min-width: 1370px)")


if (mediaQuery.matches) {
    toggleSidebar(false)
} else {
    toggleSidebar(true)
}

mediaQuery.addEventListener('change', e => {
    if (e.matches) {
        toggleSidebar(false)
    } else {
        toggleSidebar(true)
    }
});

function toggleSidebar(hide= null){
    const sidebar = document.getElementById('sc-sidebar');
    const contents = document.getElementById('sc-content');
    let condition;

    if (hide !== null){
        condition = hide;
    } else {
        condition = !sidebar.classList.contains('hidden');
    }

    // hides
    if (condition){
        contents.style.marginLeft = '0';
        sidebar.classList.add('hidden')
        sidebar.style.left = '-200px';

    }
    else {
        contents.style.marginLeft = !mediaQuery.matches ? '0' : '250px';
        sidebar.classList.remove('hidden')
        sidebar.style.left = '';
    }
}
function initializeAllComponents() {
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.onclick = function () {
            const row = btn.closest('tr');
            row.querySelectorAll(".copy").forEach(copySpan => {
                copySpan.classList.add("disabled")
            });
            row.querySelectorAll(':not(.inpt-wrapper) > input').forEach(function (i) {
                i.disabled = false;
                const wrapper = i.closest('.user-select-none');
                wrapper.classList.remove('user-select-none')
                i.classList.remove('plain');
                i.classList.add('editable');
            });
            row.querySelectorAll('.inpt-wrapper').forEach(i => {
                i.classList.remove('disabled')
            });
            row.querySelector('.save-btn').style.display = 'inline';
            btn.style.display = 'none';
        };
    });
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', async e => {
            if (!confirm("Are you sure you want to delete this enrollment?")) {
                return;
            }
            const row = btn.closest('tr');
            const id = row.dataset.id;
            const table = row.dataset.table;
            const response = await fetch(`delete-${table}/${id}/`, {
                method: 'POST'
            });
            const result = await response.json();
            if (result.success) {
                row.remove()
            }
        });
    });
    document.querySelectorAll('.save-btn').forEach(btn => {
        btn.onclick = async function () {
            const row = btn.closest('tr');
            const id = row.dataset.id;
            const table = row.dataset.table;
            let data;
            if (table === "enrollment") {
                data = {
                    paid_fee: row.children[3].querySelector('input').value,
                    status: row.children[4].querySelector('.main-selected').value,
                };
            } else if (table === "student") {
                data = {
                    name: row.children[0].querySelector('input').value,
                    father_name: row.children[1].querySelector('input').value,
                    contact: row.children[4].querySelector('input').value,
                };
            }

            const response = await fetch(`update-${table}/${id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            const result = await response.json()

            if (result.success) {
                if (table === "enrollment") {
                    row.children[2].textContent = result.remaining_fee;
                }
            }
            row.querySelectorAll(".copy").forEach(copySpan => {
                copySpan.classList.remove("disabled")
            })
            row.querySelectorAll(':not(.inpt-wrapper) > input').forEach(function (i) {
                i.disabled = true;
                const wrapper = i.closest('span');
                wrapper.classList.add('user-select-none')
                i.classList.add('plain');
                i.classList.remove('editable');
            });
            row.querySelectorAll('.inpt-wrapper').forEach(i => {
                i.classList.add('disabled')
            });
            row.querySelector('.edit-btn').style.display = 'inline';
            btn.style.display = 'none';

        };
    });
    const enrollmentForm = document.getElementById('enrollments-filer-form');
    if (enrollmentForm) {
        enrollmentForm.onsubmit = async function (e) {
            e.preventDefault();
            const startDate = document.getElementById('start-date').value;
            const endDate = document.getElementById('end-date').value;
            const selectedStatuses = Array.from(document.querySelectorAll('.mcq-list li .checked')).map(spn => spn.dataset.value);
            await addFilter(startDate, endDate, selectedStatuses);
        }
    }


    document.querySelectorAll(".sc-sidebar-links li a").forEach(link => {
        link.onclick = function () {
            document.querySelectorAll(".sc-sidebar-links li a").forEach(l => l.classList.remove("active"));
            this.classList.add("active");
        }
    });


    document.querySelectorAll('.search-bar').forEach(bar => {
        bar.addEventListener('input', function (e) {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll(`#${bar.dataset.name}-data-row`);
            rows.forEach(row => {
                const search = row.dataset.search.toLowerCase();
                if (search.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    })

    document.querySelectorAll('.check-box').forEach(checkbox => {
        checkbox.addEventListener('click', function (e) {
            if (e.target.classList.contains('checked')) {
                e.target.classList.remove('checked');
            } else {
                e.target.classList.add('checked');
            }
        });
    });


    document.querySelectorAll('.copy').forEach(elmt => {
        elmt.addEventListener('click', async () => {
            if (elmt.classList.contains("disabled")) {
                return
            }
            const text = elmt.dataset.copy;
            const row = elmt.closest('td');
            try {
                await navigator.clipboard.writeText(text);
                elmt.id = "visible";
                row.style.overflow = "visible";
                await sleep(1000);
                row.style.overflow = "hidden";
                elmt.id = "";
            } catch (err) {
                console.error('Failed to copy: ', err);
            }
        });
    });

    initDropdowns();
}

document.querySelector('.profile-icon').addEventListener('click', function () {
    const dropdown = document.querySelector('.profile-dropdown');
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
});

// Close the dropdown if clicked outside
document.addEventListener('click', function (event) {
    const profileIcon = document.querySelector('.profile-icon');
    const profDropdown = document.querySelector('.profile-dropdown');
    const dropdowns = document.querySelectorAll('.drpdwn');

    dropdowns.forEach((dropdown) => {
        const options = dropdown.querySelector('.drpdwn-optns');
        if (options.style.display === 'block' && !dropdown.contains(event.target)) {
            hideOptions(dropdown)
        }
    });

    if (!profileIcon.contains(event.target) && !profDropdown.contains(event.target)) {
        profDropdown.style.display = 'none';
    }
});

function refreshCache (){
  console.log('ran');
  fetch('refresh-cache/').catch(err => console.error(err));
}
setInterval(refreshCache, 60 * 10000);

document.addEventListener('DOMContentLoaded', initializeAllComponents);
document.addEventListener('DOMContentLoaded', refreshCache);
document.body.addEventListener('htmx:afterSwap', initializeAllComponents);

