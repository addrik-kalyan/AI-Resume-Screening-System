document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("upload-form");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    const input = document.getElementById("resume-input");
    const file = input.files[0];

    if (!file) {
      alert("Please choose a resume file first.");
      e.preventDefault();
      return;
    }

    const allowed = [".pdf", ".docx"];
    const isAllowed = allowed.some((ext) => file.name.toLowerCase().endsWith(ext));
    if (!isAllowed) {
      alert("Only PDF or DOCX files are supported.");
      e.preventDefault();
      return;
    }

    const maxSizeMB = 5;
    if (file.size > maxSizeMB * 1024 * 1024) {
      alert(`File is too large. Max size is ${maxSizeMB}MB.`);
      e.preventDefault();
    }
  });
});
