document.addEventListener("DOMContentLoaded", () => {
  const addNoteForm = document.getElementById("add-note-form");
  const notesDisplayArea = document.getElementById("notes-display-area");
  const noteTextInput = document.getElementById("note-text");
  const houseIdInput = document.getElementById("houseId");

  if (addNoteForm) {
    addNoteForm.addEventListener("submit", async (event) => {
      event.preventDefault(); // Prevent default form submission

      const noteText = noteTextInput.value.trim();
      const houseId = houseIdInput.value;

      if (!noteText) {
        alert("備註內容不能為空！");
        return;
      }

      if (!houseId) {
        alert("無法獲取房屋ID，請刷新頁面再試。");
        return;
      }

      try {
        const response = await fetch("/api/add_note", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            house_id: houseId,
            content: noteText,
          }),
        });

        if (response.ok) {
          const newNote = await response.json(); // Assuming the backend returns the new note object

          // Create new note element and add it to the display area
          const noteElement = document.createElement("div");
          noteElement.classList.add("existing-note");

          const noteContent = document.createElement("p");
          noteContent.textContent = newNote.content; // Adjust if your backend returns a different structure

          const noteTimestamp = document.createElement("span");
          // Format date as needed, or use the one from backend if available
          noteTimestamp.textContent = ` 備註於: ${
            newNote.created_at || new Date().toLocaleString()
          }`;

          noteContent.innerHTML += ` <span>${noteTimestamp.textContent}</span>`;
          noteElement.appendChild(noteContent);

          // If there's a "目前沒有備註" message, remove it
          const noNotesMessage = notesDisplayArea.querySelector("p");
          if (
            noNotesMessage &&
            noNotesMessage.textContent === "目前沒有備註。"
          ) {
            noNotesMessage.remove();
          }

          notesDisplayArea.appendChild(noteElement); // Changed from appendChild to prepend
          noteTextInput.value = ""; // Clear the textarea
          // alert('備註已成功新增！'); // Optional: show a success message
        } else {
          const errorData = await response.json();
          alert(`新增備註失敗: ${errorData.message || response.statusText}`);
        }
      } catch (error) {
        console.error("新增備註時發生錯誤:", error);
        alert("新增備註時發生網路或伺服器錯誤。");
      }
    });
  }
});
