console.log("Script loaded!"); // Debugging

function formatKey(key) {
    return key.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

document.addEventListener("DOMContentLoaded", function () {
    const cardRow = document.querySelector(".card-row");
    const leftArrow = document.querySelector(".left-arrow"); // Update with correct class
    const rightArrow = document.querySelector(".right-arrow"); // Update with correct class

    if (cardRow && leftArrow && rightArrow) {
        leftArrow.addEventListener("click", function () {
            cardRow.scrollBy({ left: -300, behavior: "smooth" }); // Adjust scroll amount if needed
        });

        rightArrow.addEventListener("click", function () {
            cardRow.scrollBy({ left: 300, behavior: "smooth" }); // Adjust scroll amount if needed
        });
    }
});


document.addEventListener("DOMContentLoaded", function () {
    const cardRow = document.querySelector(".card-row");
    if (cardRow) {
        cardRow.style.overflowX = "hidden";
        cardRow.style.whiteSpace = "nowrap"; // Prevents items from wrapping
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const recommendationContainer = document.getElementById("recommendation-container");
    const leftArrow = document.querySelector(".left-btn");
    const rightArrow = document.querySelector(".right-btn");

    if (recommendationContainer && leftArrow && rightArrow) {
        leftArrow.addEventListener("click", function () {
            recommendationContainer.scrollBy({ left: -300, behavior: "smooth" });
        });

        rightArrow.addEventListener("click", function () {
            recommendationContainer.scrollBy({ left: 300, behavior: "smooth" });
        });
    } else {
        console.error("❌ Arrow buttons or container not found.");
    }
});


document.addEventListener("DOMContentLoaded", async () => {
    if (window.location.pathname === "/") {
        console.log("Login page detected. Setting up login function.");

        document.getElementById("login-btn").addEventListener("click", login);
    }

    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-btn");
    const chatContainer = document.getElementById("chat-container");
    const chatToggle = document.getElementById("chat-toggle");
    const closeChat = document.getElementById("close-chat");
    const profilePic = document.getElementById("profile-pic");
    const dropdown = document.getElementById("profile-dropdown");
    const editButton = document.getElementById("edit-profile");
    const saveButton = document.getElementById("save-profile");
    const userName = document.getElementById("user-name");
    const userContact = document.getElementById("user-contact");
    const userId = document.getElementById("user-id");
    const userAddress = document.getElementById("user-address");
    const userContent = document.getElementById("user-content");
    const closeButton = document.getElementById("close-profile");
    const logoutButton = document.getElementById("logout-btn")
    const modal = document.getElementById("custom-modal");
    const modalTitle = document.getElementById("modal-title");
    const modalDescription = document.getElementById("modal-description");
    const closeModalButton = document.getElementById("close-modal");
    const closeIcon = document.querySelector(".close-modal");

    
    // Load user data
    try {
        const userResponse = await fetch("../user_schema.json");
        if (!userResponse.ok) throw new Error("User not authenticated");
        const userData = await userResponse.json();
        const user = userData.Customer;
        if (user) {
            userName.textContent = user.full_name || "N/A";
            userContact.textContent = user.phone_number || "N/A";
            userAddress.textContent = `${user.address.city}, ${user.address.country}` || "N/A";
        }
        document.getElementById("user-name").textContent = user.full_name;
        document.getElementById("user-contact").textContent = user.phone_number;
    } catch (error) {
        console.error("Error loading user data:", error);
        window.location.href = "/";
    }

    

    
    if (profilePic && dropdown) {
        profilePic.addEventListener("click", () => dropdown.classList.toggle("show"));
        document.addEventListener("click", (event) => {
            if (!profilePic.contains(event.target) && !dropdown.contains(event.target)) {
                dropdown.classList.remove("show");
            }
        });
    }

    // Close button functionality
    if (closeButton) {
        closeButton.addEventListener("click", () => {
            dropdown.classList.remove("show");
        });
    }

    // Logout button functionality
    logoutButton.addEventListener("click", function () {
        window.location.href = "/logout"; // Redirect to Flask logout route
    });
    

    // Load Financial Products
    try {
        const response = await fetch("/home");
        if (!response.ok) throw new Error("User not authenticated");
        
        const text = await response.text();
        console.log("HTML response successfully parsed.");
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, "text/html");
        const recommendationDataElement = doc.getElementById("recommendation-data");

        if (!recommendationDataElement) {
            throw new Error("❌ Element with ID 'recommendation-data' not found.");
        }

        const recommendations = JSON.parse(recommendationDataElement.textContent);
        const recommendationContainer = document.getElementById("recommendation-container");
        recommendationContainer.innerHTML = "";

        const allProducts = Object.values(recommendations).flat();
        if (allProducts.length === 0) {
            recommendationContainer.innerHTML = "<p>No recommendations available at this time.</p>";
            return;
        }

        allProducts.forEach((product) => {
            const card = createCard(product);
            recommendationContainer.appendChild(card);
        });

        const loveContainer = document.getElementById("love-container");
        loveContainer.innerHTML = "";
        allProducts.slice(0, 5).forEach((product) => {
            const card = createCard(product);
            loveContainer.appendChild(card);
        });
    } catch (error) {
        console.error("🚨 Error loading financial products:", error);
    }

    // Function to Create a Card
    function createCard(product) {
        const card = document.createElement("div");
        card.classList.add("card");
        card.innerHTML = `
            <h3>${product.name}</h3>
            <p><strong>About:</strong> ${product.about}</p>
            <p><strong>Eligible:</strong> ${product.eligible_customers || "N/A"}</p>
            <p class="modal-trigger"><strong>Click here for more info!</strong></p>
        `;
    
        // Add event listener to open modal when clicking "Click here for more info!"
        const trigger = card.querySelector(".modal-trigger");
        trigger.addEventListener("click", function () {
            modalTitle.textContent = product.name;
            // Convert all key-value pairs into HTML content
            let descriptionHTML = `<p>${product.about}</p>`;
            for (const [key, value] of Object.entries(product)) {
                if (key == 'about' || key == 'name') continue;
                else if (value) {  // Only show non-null values
                    descriptionHTML += `<p><strong>${formatKey(key)}:</strong> ${value}</p>`;
                }
            }

            modalDescription.innerHTML = descriptionHTML; // Set modal content

            modal.style.display = "flex"; // Show modal
        });
    
        return card;
    }

    // Close Modal on Button Click
    closeModalButton.addEventListener("click", function () {
        modal.style.display = "none";
    });

    // Close Modal on 'X' Click
    closeIcon.addEventListener("click", function () {
        modal.style.display = "none";
    });

    // Close Modal on Outside Click
    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
    

    // Toggle chat window
    chatToggle.addEventListener("click", () => {
        chatContainer.classList.toggle("hidden");
    });

    // Close chat window
    closeChat.addEventListener("click", () => {
        chatContainer.classList.add("hidden");
    });

    function appendMessage(role, text) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", role === "user" ? "user-message" : "bot-message");
        messageDiv.innerText = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function appendProductRecommendation(products) {
        const cardContainer = document.createElement("div");
        cardContainer.classList.add("product-container");

        products.forEach(product => {
            const card = document.createElement("div");
            card.classList.add("product-card");

            card.innerHTML = `
                <h4>
                    <a href="product.html?name=${encodeURIComponent(product.name)}" target="_blank">
                        ${product.name}
                    </a>
                </h4>
                <p>${product.reason}</p>
            `;

            cardContainer.appendChild(card);
        });

        chatBox.appendChild(cardContainer);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    sendButton.addEventListener("click", async () => {
        const message = userInput.value.trim();
        if (!message) return;

        appendMessage("user", message);
        userInput.value = "";
        sendButton.disabled = true;

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            if (typeof data === "string") {
                appendMessage("bot", data);
            } else if (data.products && Array.isArray(data.products)) {
                appendProductRecommendation(data.products);
            } else {
                appendMessage("bot", "Unexpected response format.");
            }
        } catch (error) {
            appendMessage("bot", "Error connecting to the server.");
        }

        sendButton.disabled = false;
    });

    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendButton.click();
        }
    });
});


