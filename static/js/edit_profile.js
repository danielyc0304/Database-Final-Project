document.addEventListener("DOMContentLoaded", () => {
  console.log("DOMContentLoaded event fired");
  const editProfileForm = document.getElementById("edit-profile-form");
  console.log(
    "Attempting to find form with ID edit-profile-form:",
    editProfileForm
  );

  const messageArea = document.getElementById("message-area");
  console.log(
    "Attempting to find message area with ID message-area:",
    messageArea
  );

  if (editProfileForm) {
    console.log("Form element found, attaching event listener");
    editProfileForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      messageArea.innerHTML = ""; // Clear previous messages

      const formData = new FormData(editProfileForm);

      // --- Log formData entries for debugging ---
      console.log("Form Data to be sent:");
      for (let [key, value] of formData.entries()) {
        console.log(key, value);
      }
      // --- End log ---

      try {
        const response = await fetch("/api/profile/update", {
          method: "POST",
          body: formData,
        });

        const result = await response.json();
        // --- Log received result for debugging ---
        console.log("Received result from server:", result);
        // --- End log ---

        if (response.ok) {
          messageArea.innerHTML = `<div class="message success">${
            result.message || "個人檔案更新成功！"
          }</div>`;
          if (
            result.new_avatar_url &&
            document.getElementById("avatar-preview-img")
          ) {
            const currentAvatarSrc =
              document.getElementById("avatar-preview-img").src;
            // Update preview only if it's a new URL and not just a local blob preview
            if (result.new_avatar_url.startsWith("http")) {
              document.getElementById("avatar-preview-img").src =
                result.new_avatar_url;
            }
          }
        } else {
          messageArea.innerHTML = `<div class="message error">${
            result.error || "更新失敗，請再試一次。"
          }</div>`;
        }
      } catch (error) {
        console.error("Error updating profile:", error);
        messageArea.innerHTML = `<div class="message error">更新時發生錯誤，請檢查網路連線。</div>`;
      }
    });
  } else {
    console.log("Form element with ID edit-profile-form NOT found!"); // 新增的 log
  }

  // Avatar preview logic
  const avatarInput = document.getElementById("avatar");
  const avatarPreview = document.getElementById("avatar-preview-img");

  if (avatarInput && avatarPreview) {
    avatarInput.addEventListener("change", function (event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          avatarPreview.src = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    });
  }
});
