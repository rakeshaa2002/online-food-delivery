document.querySelectorAll('.food-card button').forEach(button => {
    button.addEventListener('click', () => {
        const foodId = button.getAttribute('data-food-id');
        fetch(`/add-to-cart/${foodId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showPopup(data.message); // Just show the popup, no redirect
            }
        })
        .catch(error => {
            showPopup("Failed to add item to cart.");
            console.error('Error:', error);
        });
    });
});

function updateQuantity(cartId) {
    const qty = document.getElementById('qty-' + cartId).value;
    fetch(`/update-cart-quantity/${cartId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ quantity: qty })
    })
    .then(response => response.json())
    .then(data => {
        showPopup(data.message || "Quantity updated!", function() {
            location.reload();
        });
    })
    .catch(error => {
        showPopup("Failed to update quantity.");
        console.error('Error:', error);
    });
}

function deleteItem(cartId) {
    showPopup("Are you sure you want to remove this item from the cart?", function() {
        fetch(`/delete-cart-item/${cartId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            }
        })
        .then(response => response.json())
        .then(data => {
            showPopup(data.message || "Item removed!", function() {
                location.reload();
            });
        })
        .catch(error => {
            showPopup("Failed to remove item.");
            console.error('Error:', error);
        });
    });
}

function showPaymentOptions() {
    document.getElementById('place-order-btn').style.display = 'none';
    document.getElementById('payment-options').style.display = 'block';
}

function submitOrder(paymentMethod) {
    if (paymentMethod === 'online') {
        fetch('/create-stripe-session/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.session_url) {
                window.location.href = data.session_url;
            } else {
                showPopup(data.message || "Failed to start payment.");
            }
        })
        .catch(error => {
            showPopup("Failed to start payment.");
            console.error('Error:', error);
        });
    } else {
        fetch('/place-order/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ payment_method: paymentMethod })
        })
        .then(response => response.json())
        .then(data => {
            if (data.redirect_url) {
                showPopup(data.message || "Order placed!", function() {
                    window.location.href = data.redirect_url;
                });
            } else if (data.message && data.message.toLowerCase().includes('cart is empty')) {
                showPopup(data.message, function() {
                    window.location.href = '/cart/';
                });
            } else {
                showPopup(data.message || "Order placed!");
            }
        })
        .catch(error => {
            showPopup("Failed to place order.");
            console.error('Error:', error);
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var placeOrderBtn = document.getElementById('place-order-btn');
    var emptyCartMsg = document.getElementById('empty-cart-msg');
    if (placeOrderBtn) {
        placeOrderBtn.addEventListener('click', function(event) {
            if (emptyCartMsg && emptyCartMsg.style.display !== 'none') {
                event.preventDefault();
                showPopup("Cart is empty!");
            }
        });
    }
});

// Helper function to get CSRF token
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}

// Show custom popup with message and optional callback for OK
function showPopup(message, onOk) {
    const popup = document.getElementById('custom-popup');
    const msg = document.getElementById('custom-popup-message');
    const okBtn = document.getElementById('custom-popup-ok');
    msg.textContent = message;
    popup.style.display = 'flex';
    okBtn.onclick = function() {
        popup.style.display = 'none';
        if (typeof onOk === 'function') onOk();
    };
}

function deleteOrder(orderId) {
    if (!confirm("Are you sure you want to delete this order history?")) return;
    fetch(`/delete-order/${orderId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(response => response.json())
    .then(function(data) {
        document.getElementById('custom-popup-message').innerText = data.message || "Order deleted!";
        document.getElementById('custom-popup').style.display = 'flex';
        setTimeout(() => {
            location.reload();
        }, 1500);
    })
    .catch(error => {
        showPopup("Failed to delete order.");
        console.error('Error:', error);
    });
}


