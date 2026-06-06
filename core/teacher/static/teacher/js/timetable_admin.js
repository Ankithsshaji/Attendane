document.addEventListener("DOMContentLoaded", function () {

    const department = document.getElementById("id_department");
    const classRoom = document.getElementById("id_class_room");
    const subject = document.getElementById("id_subject");

    if (!department || !classRoom || !subject) return;

    const allClassOptions = Array.from(classRoom.options);
    const allSubjectOptions = Array.from(subject.options);

    function filterData() {
        const deptText = department.options[department.selectedIndex].text.trim().toUpperCase();

        classRoom.innerHTML = "";
        subject.innerHTML = "";

        allClassOptions.forEach(option => {
            const text = option.text.trim().toUpperCase();

            if (option.value === "" || text.includes(deptText)) {
                classRoom.appendChild(option.cloneNode(true));
            }
        });

        allSubjectOptions.forEach(option => {
            const text = option.text.trim().toUpperCase();

            if (option.value === "" || text.includes(deptText)) {
                subject.appendChild(option.cloneNode(true));
            }
        });
    }

    department.addEventListener("change", filterData);
    filterData();

});