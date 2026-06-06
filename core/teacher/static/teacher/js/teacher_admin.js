document.addEventListener("DOMContentLoaded", function () {

    const departments = document.getElementById("id_departments_from");
    const classes = document.getElementById("id_classes_from");
    const subjects = document.getElementById("id_subjects_from");

    if (!departments || !classes || !subjects) return;

    const allClasses = Array.from(classes.options);
    const allSubjects = Array.from(subjects.options);

    function getChosenDepartments() {
        const chosen = document.getElementById("id_departments_to");

        return Array.from(chosen.options).map(option =>
            option.text.trim().toUpperCase()
        );
    }

    function filterData() {
        const selectedDepartments = getChosenDepartments();

        classes.innerHTML = "";
        subjects.innerHTML = "";

        allClasses.forEach(option => {
            const text = option.text.trim().toUpperCase();

            if (
                selectedDepartments.includes("MCA") &&
                text.includes("MCA")
            ) {
                classes.appendChild(option.cloneNode(true));
            }

            if (
                selectedDepartments.includes("BCA") &&
                text.includes("BCA")
            ) {
                classes.appendChild(option.cloneNode(true));
            }
        });

        allSubjects.forEach(option => {
            const text = option.text.trim().toUpperCase();

            if (
                selectedDepartments.includes("MCA") &&
                text.includes("MCA")
            ) {
                subjects.appendChild(option.cloneNode(true));
            }

            if (
                selectedDepartments.includes("BCA") &&
                text.includes("BCA")
            ) {
                subjects.appendChild(option.cloneNode(true));
            }
        });
    }

    document.addEventListener("click", function () {
        setTimeout(filterData, 200);
    });

    filterData();

});