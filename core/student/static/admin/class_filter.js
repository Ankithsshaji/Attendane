document.addEventListener("DOMContentLoaded", function () {

    console.log("JS LOADED");

    const deptField = document.getElementById("id_department");
    const classField = document.getElementById("id_class_name");

    if (!deptField || !classField) return;

    deptField.addEventListener("change", function () {

        const deptId = this.value;

        classField.innerHTML = '<option value="">Select Class</option>';

        if (!deptId) return;

        fetch(`/ajax/load-classes/?department_id=${deptId}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(item => {
                    const option = document.createElement("option");
                    option.value = item.id;
                    option.textContent = item.name;
                    classField.appendChild(option);
                });
            });

    });

});