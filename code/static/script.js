console.log("Script loaded!"); // Debugging

function formatKey(key) {
    return key.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

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
    const userName = document.getElementById("user-name");
    const userContact = document.getElementById("user-contact");
    const userId = document.getElementById("user-id");
    const userAddress = document.getElementById("user-address");
    const userContent = document.getElementById("user-content");
    const closeButton = document.getElementById("close-profile");
    const logoutButton = document.getElementById("logout-btn");
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

    // Logout Functionality
    logoutButton.addEventListener("click", function () {
        window.location.href = "/logout";
    });

    // Load Financial Products
    try {
        const response = await fetch("/home");
        console.log("Response received:", response);
    
        if (!response.ok) throw new Error("User not authenticated");
    
        // Parse HTML response
        const text = await response.text();
        console.log("HTML response successfully parsed.");
    
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, "text/html");
    
        // Extract user recommendations
        const userRecElement = doc.getElementById("user-recommendation-data");
        if (!userRecElement) throw new Error("Element 'user-recommendation-data' not found.");
        const userRecommendations = JSON.parse(userRecElement.textContent);
    
        // Extract relationship-based recommendations
        const relationshipRecElement = doc.getElementById("relationship-recommendation-data");
        if (!relationshipRecElement) throw new Error("Element 'relationship-recommendation-data' not found.");
        const relationshipRecommendations = JSON.parse(relationshipRecElement.textContent);

         // Extract relationship-based recommendations
         const healthcareRecElement = doc.getElementById("healthcare-recommendation-data");
         if (!healthcareRecElement) throw new Error("Element 'healthcare-recommendation-data' not found.");
         const healthcareRecommendations = JSON.parse(healthcareRecElement.textContent);
    
        console.log("User Recommendations:", userRecommendations);
        console.log("Relationship Recommendations:", relationshipRecommendations);
        console.log("Healthcare Recommendations:", healthcareRecommendations);
        
        // Populate "Recommendations for You"
        const userRecContainer = document.getElementById("recommendation-container");
        userRecContainer.innerHTML = ""; 
    
        const userProducts = Object.values(userRecommendations).flat();
        if (userProducts.length === 0) {
            console.warn("No recommendations found.");
            userRecContainer.innerHTML = "<p>No recommendations available at this time.</p>";
        } else {
            const userProductRow = document.createElement("div");
            userProductRow.classList.add("card-row");
    
            userProducts.forEach((product) => {
                console.log("Adding User Product:", product.name);
                const card = createCard(product);
                userProductRow.appendChild(card);
            });
    
            userRecContainer.appendChild(userProductRow);
        }
    
        const relationshipRecContainer = document.getElementById("love-container");
        relationshipRecContainer.innerHTML = ""; 
    
        const relationshipProducts = Object.values(relationshipRecommendations).flat();
        if (relationshipProducts.length === 0) {
            console.warn("No relationship recommendations found.");
            relationshipRecContainer.innerHTML = "<p>No recommendations available for your loved ones at this time.</p>";
        } else {
            const relationshipProductRow = document.createElement("div");
            relationshipProductRow.classList.add("card-row");
    
            relationshipProducts.forEach((product) => {
                console.log("Adding Relationship Product:", product.name);
                const card = createCard(product);
                relationshipProductRow.appendChild(card);
            });
    
            relationshipRecContainer.appendChild(relationshipProductRow);
        }

        const healthcareRecContainer = document.getElementById("healthcare-container");
        healthcareRecContainer.innerHTML = ""; 
    
        const healthcareProducts = Object.values(healthcareRecommendations).flat();
        if (healthcareProducts.length === 0) {
            console.warn("No relationship recommendations found.");
            healthcareRecContainer.innerHTML = "<p>No recommendations available for your loved ones at this time.</p>";
        } else {
            const healthcareProductRow = document.createElement("div");
            healthcareProductRow.classList.add("card-row");
    
            healthcareProducts.forEach((product) => {
                console.log("Adding Relationship Product:", product.name);
                const card = createServicesCard(product);
                healthcareProductRow.appendChild(card);
            });
    
            healthcareRecContainer.appendChild(healthcareProductRow);
        }
    
        console.log("Recommendations Loaded Successfully!");
    
    } catch (error) {
        console.error("Error loading financial products:", error);
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

        card.querySelector(".modal-trigger").addEventListener("click", function () {
            modalTitle.textContent = product.name;
            let descriptionHTML = `<p>${product.about}</p>`;
            for (const [key, value] of Object.entries(product)) {
                if (key !== "about" && key !== "name" && value && key !=="category") {
                    descriptionHTML += `<p><strong>${formatKey(key)}:</strong> ${value}</p>`;
                }
            }
            modalDescription.innerHTML = descriptionHTML;
            modal.style.display = "flex";
        });

        return card;
    }
    
    // Function to Create a Card
    function createServicesCard(product) {
        const card = document.createElement("div");
        card.classList.add("card");
        card.innerHTML = `
            <h3>${product.service}</h3>
            <p><strong>Reason:</strong> ${product.reason}</p>
        `;
        return card;
    }
    
    // Close Modal Handlers
    closeModalButton.addEventListener("click", () => (modal.style.display = "none"));
    closeIcon.addEventListener("click", () => (modal.style.display = "none"));
    window.addEventListener("click", (event) => {
        if (event.target === modal) modal.style.display = "none";
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


