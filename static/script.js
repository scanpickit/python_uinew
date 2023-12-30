window.onload = function () {
    document.documentElement.classList.add('loaded');

    if (document.querySelector('.product_slider')) {
        new Swiper('.product_slider', {
            loop: true,
            direction: 'horizontal',
            slidesPerView: 1,
            spaceBetween: 30,
            speed: 1000,
            parallax: true,
            mouseWheel: true,
            keyboard: {
                enabled: true,
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            on: {
                init: function () {
                    console.log('initiated');
                },
            },
        });
    }

    const cart = document.querySelector('.header_cart');
    const cartValue = document.querySelector('.header_cart span');
    const sideMenu = document.querySelector('.side-menu .cart-content');
    const totalDisplay = document.getElementById('amt');
    const emptyCartMsg = document.getElementById('emptyCartMsg');
    const speedAnimation = 1000;
    const cartPos = {
        left: sideMenu.getBoundingClientRect().left,
        top: sideMenu.getBoundingClientRect().top,
    };

    let totalAmount = 0;
    let totalQuantity = 0;

    document.addEventListener('click', function (e) {
        const targetElement = e.target;

        if (targetElement.classList.contains('product_buy') || targetElement.classList.contains('buy-now')) {
            const productSlide = targetElement.closest('.product_slide');
            const productTitle = productSlide.querySelector('.product_title').textContent;
            const productPrice = parseFloat(productSlide.querySelector('.product_price').textContent.replace('Rs.', ''));
            const productImageSrc = productSlide.querySelector('.product_picture').src;

            const existingCartItem = findCartItem(productTitle);

            if (existingCartItem) {
                console.log('incremented');
                incrementCartValue(productTitle, productPrice, productImageSrc);
            } else {
                addToCart(productTitle, productPrice, productImageSrc);
            }

            const isEmptyCart = sideMenu.childElementCount === 0;

            if (isEmptyCart) {
                const initialText = sideMenu.querySelector('p');
                if (initialText) {
                    emptyCartMsg.style.display = 'block';
                }
            }

            const productImage = productSlide.querySelector('.product_picture');
            const productImageFly = productImage.cloneNode(true);

            productImageFly.style.cssText = `
                position: fixed;
                left: ${productImage.getBoundingClientRect().left}px;
                top: ${productImage.getBoundingClientRect().top}px;
                width: ${productImage.offsetWidth}px;
                height: ${productImage.offsetHeight}px;
                transition: all ${speedAnimation}ms ease;
            `;

            document.body.append(productImageFly);

            setTimeout(() => {
                productImageFly.style.left = `${cartPos.left}px`;
                productImageFly.style.top = `${cartPos.top}px`;
                productImageFly.style.width = `0px`;
                productImageFly.style.height = `0px`;
                productImageFly.style.opacity = `0.5`;
            }, 0);

            totalQuantity += 1;
            totalAmount += productPrice;
        } else if (targetElement.classList.contains('remove-item')) {
            const cartItem = targetElement.closest('p');

            if (cartItem) {
                const removedQuantity = parseInt(cartItem.querySelector('.quantity').textContent, 10);
                const removedPrice = parseFloat(cartItem.querySelector('.cart-item-price').textContent.replace('Rs.', ''));

                cartItem.parentNode.removeChild(cartItem);

                totalQuantity -= removedQuantity;
                totalAmount -= removedPrice * removedQuantity;

                if (sideMenu.childElementCount === 0) {
                    const initialText = document.createElement('p');
                    initialText.textContent = 'Your cart is empty.';
                    sideMenu.appendChild(initialText);
                    emptyCartMsg.style.display = 'none';
                }
            }
        }

        updateHeaderCart();
        updateSideMenuTotal();
    });

    function findCartItem(productTitle) {
        return Array.from(sideMenu.querySelectorAll('.cart-item-title')).find(title => title.textContent === productTitle);
    }

    function incrementCartValue(productTitle, productPrice, productImageSrc) {
        const existingCartItem = findCartItem(productTitle);
    
        if (existingCartItem) {
            // If the product already exists, increment the quantity by 1
            const quantityElement = existingCartItem.querySelector('.quantity');
            let quantity = parseInt(quantityElement.textContent, 10);
            quantity += 1;
            quantityElement.textContent = quantity;
    
            updateCartItemTotal(existingCartItem, quantity, productPrice);
        } else {
            // If the product does not exist, add it to the cart with a quantity of 1
            addToCart(productTitle, productPrice, productImageSrc);
        }
    
        // Update the total quantity and amount
        totalQuantity += 1;
        totalAmount += productPrice;
    
        // Update the header cart and side menu total
        updateHeaderCart();
        updateSideMenuTotal();
    }
    

    function addToCart(productTitle, productPrice, productImageSrc) {
        const cartItem = document.createElement('div');
        const quantity = 1;

        cartItem.innerHTML = `
            <p>
                <img src="${productImageSrc}" alt="Product Image" class="cart-item-image">
                <span class="cart-item-details">
                    <span class="cart-item-title">${productTitle}</span>
                    <span class="cart-item-price">Rs.${productPrice.toFixed(2)}</span>
                </span>
                <span class="quantity-group">
                    <button class="btn btn-primary">-</button>
                    <span class="quantity" style="font-size: 1.5rem;">${quantity}</span>
                    <button class="btn btn-primary">+</button>
                </span>
                <span class="cart-item-total">Rs.${productPrice.toFixed(2)}</span>
            </p>
        `;

        sideMenu.appendChild(cartItem);

        const quantityButtons = cartItem.querySelectorAll('.quantity-group button');
        quantityButtons.forEach(button => {
            button.addEventListener('click', function () {
                const cartItem = this.closest('p');
                const quantityElement = cartItem.querySelector('.quantity');
                let quantity = parseInt(quantityElement.textContent, 10);

                if (this.textContent === '-') {
                    quantity = Math.max(0, quantity - 1);
                    quantityElement.textContent = quantity;
                } else if (this.textContent === '+') {
                    quantity += 1;
                    quantityElement.textContent = quantity;
                }

                updateCartItemTotal(cartItem, quantity, productPrice);

                if (quantity === 0) {
                    cartItem.parentNode.removeChild(cartItem);
                }

                totalQuantity = Array.from(sideMenu.querySelectorAll('.quantity')).reduce((sum, el) => sum + parseInt(el.textContent, 10), 0);
                totalAmount = Array.from(sideMenu.querySelectorAll('.cart-item-total')).reduce((sum, el) => sum + parseFloat(el.textContent.replace('Rs.', '')), 0);

                updateHeaderCart();
                updateSideMenuTotal();
            });
        });
    }

    function updateHeaderCart() {
        const cartValue = document.querySelector('.header_cart span');
        cartValue.innerHTML = totalQuantity;
    }

    function updateSideMenuTotal() {
        const sideMenuTotal = document.getElementById('amt');
        sideMenuTotal.innerHTML = `Rs.${totalAmount.toFixed(2)}`;
    }

    function updateCartItemTotal(cartItem, quantity, productPrice) {
        const itemTotalPrice = quantity * productPrice;
        cartItem.querySelector('.cart-item-total').textContent = `Rs.${itemTotalPrice.toFixed(2)}`;
    }

    document.getElementById('overlay').addEventListener('click', function () {
        toggleOverlay();
    });

    // Submit button click event
    const submitBtn = document.querySelector('.submit-btn');
    submitBtn.addEventListener('click', function () {
        const cartItems = Array.from(sideMenu.querySelectorAll('.cart-item-title'));
        const cartQuantities = Array.from(sideMenu.querySelectorAll('.quantity'));

        const cartData = {};

        cartItems.forEach((item, index) => {
            const productTitle = item.textContent.trim();
            const productQuantity = parseInt(cartQuantities[index].textContent, 10);
            cartData[productTitle] = productQuantity;
        });

        // Add the logic for creating the form and submitting it
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = '/create_order';

        var hiddenAmountField = document.createElement('input');
        hiddenAmountField.type = 'hidden';
        hiddenAmountField.name = 'order_amount';
        hiddenAmountField.value = totalAmount.toString();

        var hiddenQuantityField = document.createElement('input');
        hiddenQuantityField.type = 'hidden';
        hiddenQuantityField.name = 'order_quantity';
        hiddenQuantityField.value = totalQuantity.toString();

        var hiddenCartDataField = document.createElement('input');
        hiddenCartDataField.type = 'hidden';
        hiddenCartDataField.name = 'cart_data';
        hiddenCartDataField.value = JSON.stringify(cartData);

        form.appendChild(hiddenAmountField);
        form.appendChild(hiddenQuantityField);
        form.appendChild(hiddenCartDataField);

        document.body.appendChild(form);
        form.submit();
    });
};

function toggleOverlay() {
    var overlay = document.getElementById('overlay');
    var sideMenu = document.getElementById('sideMenu');

    overlay.style.display = (overlay.style.display === 'block') ? 'none' : 'block';
    sideMenu.style.right = (sideMenu.style.right === '0px') ? '-1000px' : '0px';
}
