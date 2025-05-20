const uploadInput = document.getElementById("video-upload");
const resultsContainer = document.getElementById("video-results");
const totalVideosSpan = document.getElementById("total-videos");
const totalViolationsSpan = document.getElementById("total-violations");

let totalVideos = 0;
let totalViolations = 0;

const vehicleTypes = ["Xe máy", "Ô tô", "Xe tải", "Xe buýt"];
const plateSamples = ["29A12345", "30F67890", "51B23456", "36H88888"];
const violations = ["Vượt đèn đỏ", "Không phát hiện"];

uploadInput.addEventListener("change", (event) => {
  const files = Array.from(event.target.files);

  files.forEach((file) => {
    totalVideos++;
    totalVideosSpan.textContent = totalVideos;

    const row = document.createElement("div");
    row.classList.add("violation-row");
    row.style.display = "contents"; // giữ layout 4 cột grid

    // Tạo 4 card đều chứa video + thông tin cập nhật
    const cards = ["Phương tiện", "Biển số", "Loại vi phạm", "Thời gian"].map((label) => {
      const card = document.createElement("div");
      card.className = "violation-card";
      card.innerHTML = `
        <video controls src="${URL.createObjectURL(file)}"></video>
        <div class="label">${label}</div>
        <div class="value">Đang xử lý...</div>
      `;
      return card;
    });

    cards.forEach(card => row.appendChild(card));
    resultsContainer.prepend(row);

    // Giả lập xử lý sau 2 giây
    setTimeout(() => {
      const vehicleType = vehicleTypes[Math.floor(Math.random() * vehicleTypes.length)];
      const plateNumber = plateSamples[Math.floor(Math.random() * plateSamples.length)];
      const violation = violations[Math.floor(Math.random() * violations.length)];
      const time = new Date().toLocaleString();

      if (violation !== "Không phát hiện") {
        totalViolations++;
        totalViolationsSpan.textContent = totalViolations;
      }

      cards[1].querySelector(".value").textContent = plateNumber;
      cards[2].querySelector(".value").textContent = violation;
      cards[3].querySelector(".value").textContent = time;

    }, 2000);
  });
});
//--------------------------

/*

const uploadInput = document.getElementById("video-upload");
const resultsContainer = document.getElementById("video-results");
const totalVideosSpan = document.getElementById("total-videos");
const totalViolationsSpan = document.getElementById("total-violations");

let totalVideos = 0;
let totalViolations = 0;

uploadInput.addEventListener("change", (event) => {
  const files = Array.from(event.target.files);

  files.forEach((file) => {
    totalVideos++;
    totalVideosSpan.textContent = totalVideos;

    // Tạo một row hiển thị 4 ô
    const row = document.createElement("div");
    row.classList.add("violation-row");
    row.style.display = "contents";

    const cards = ["Phương tiện", "Biển số", "Loại vi phạm", "Thời gian"].map((label) => {
      const card = document.createElement("div");
      card.className = "violation-card";
      card.innerHTML = `
        <video controls src="${URL.createObjectURL(file)}"></video>
        <div class="label">${label}</div>
        <div class="value">Đang xử lý...</div>
      `;
      return card;
    });

    cards.forEach(card => row.appendChild(card));
    resultsContainer.prepend(row);

    // Gửi video đến API thực tế
    const formData = new FormData();
    formData.append("video", file);

    fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        // Gán kết quả nhận được từ API
        if (data.plate_number !== "Không rõ") {
          totalViolations++;
          totalViolationsSpan.textContent = totalViolations;
        }

        cards[1].querySelector(".value").textContent = data.plate_number || "Không rõ";
        cards[2].querySelector(".value").textContent = data.violation || "Không xác định";
        cards[3].querySelector(".value").textContent = data.time || new Date().toLocaleString();
      })
      .catch((err) => {
        console.error("Lỗi khi gửi video:", err);
        cards.forEach(card => {
          card.querySelector(".value").textContent = "Lỗi xử lý";
        });
      });
  });
});


*/