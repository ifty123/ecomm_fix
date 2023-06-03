$(document).ready(function() {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    $('.btn-increase').click(function(e) {
        e.preventDefault();
        var productId = $(this).data('product-id');
        updateQuantity(productId, 'increase');
    });

    $('.btn-decrease').click(function(e) {
        e.preventDefault();
        var productId = $(this).data('product-id');
        updateQuantity(productId, 'decrease');
    });

    function updateQuantity(productId, action) {
        $.ajax({
            url: '/update_quantity/',  // Ubah sesuai dengan URL yang tepat
            type: 'POST',
            data: {
                'product_id': productId,
                'action': action,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                // Pembaruan nilai quantity pada tabel
                $('#quantity_' + productId).text(response.quantity);
                $('#total_harga_' + productId).text("$" + response.total);
                $('#total_hemat_' + productId).text("Hemat $" + response.hemat);
                // $('#total_all_' + productId).text("$" + response.total_all);
                // $('#total_hemat_all_' + productId).text("Hemat $" + response.total_hemat);
            },
            error: function(xhr, errmsg, err) {
                console.log(errmsg);
            }
        });
    }
});
