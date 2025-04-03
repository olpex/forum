// Main JavaScript for Forum Application

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Post voting
    $('.post-upvote').click(function(e) {
        e.preventDefault();
        const postId = $(this).data('post-id');
        const url = `/posts/${postId}/upvote/`;
        
        $.post(url, function(data) {
            $(`#post-${postId}-score`).text(data.score);
            $(`#post-${postId}-upvote`).addClass('active');
            $(`#post-${postId}-downvote`).removeClass('active');
        });
    });
    
    $('.post-downvote').click(function(e) {
        e.preventDefault();
        const postId = $(this).data('post-id');
        const url = `/posts/${postId}/downvote/`;
        
        $.post(url, function(data) {
            $(`#post-${postId}-score`).text(data.score);
            $(`#post-${postId}-downvote`).addClass('active');
            $(`#post-${postId}-upvote`).removeClass('active');
        });
    });
    
    // Comment voting
    $('.comment-upvote').click(function(e) {
        e.preventDefault();
        const commentId = $(this).data('comment-id');
        const url = `/comments/${commentId}/upvote/`;
        
        $.post(url, function(data) {
            $(`#comment-${commentId}-score`).text(data.score);
            $(`#comment-${commentId}-upvote`).addClass('active');
            $(`#comment-${commentId}-downvote`).removeClass('active');
        });
    });
    
    $('.comment-downvote').click(function(e) {
        e.preventDefault();
        const commentId = $(this).data('comment-id');
        const url = `/comments/${commentId}/downvote/`;
        
        $.post(url, function(data) {
            $(`#comment-${commentId}-score`).text(data.score);
            $(`#comment-${commentId}-downvote`).addClass('active');
            $(`#comment-${commentId}-upvote`).removeClass('active');
        });
    });
    
    // Reply to comment
    $('.reply-button').click(function() {
        const commentId = $(this).data('comment-id');
        $(`#reply-form-${commentId}`).toggleClass('d-none');
    });
    
    // Tag selection and creation in post form
    if ($('#id_new_tags').length) {
        // Show/hide new tags field based on checkbox
        $('#show-new-tags').change(function() {
            if ($(this).is(':checked')) {
                $('.new-tags-field').removeClass('d-none');
            } else {
                $('.new-tags-field').addClass('d-none');
            }
        });
    }
    
    // Confirmation dialogs
    $('.confirm-action').click(function(e) {
        if (!confirm($(this).data('confirm-message') || 'Ви впевнені?')) {
            e.preventDefault();
        }
    });
    
    // Mark notification as read when clicked
    $('.notification-link').click(function() {
        const notificationId = $(this).data('notification-id');
        const url = `/notifications/${notificationId}/mark-read/`;
        
        $.post(url, function() {
            // Success callback
        });
    });
    
    // Ban duration selection
    $('#ban-type-select').change(function() {
        const value = $(this).val();
        if (value === 'temporary') {
            $('#ban-duration-group').removeClass('d-none');
        } else {
            $('#ban-duration-group').addClass('d-none');
        }
    });
    
    // Post type selection
    $('#post-type-select').change(function() {
        const value = $(this).val();
        // You can add custom logic based on post type here
    });
    
    // Search form enhancements
    $('#search-type-tabs a').click(function(e) {
        e.preventDefault();
        $(this).tab('show');
        $('#search-type').val($(this).data('search-type'));
    });
    
    // Mobile sidebar toggle
    $('#toggle-sidebar').click(function() {
        $('.sidebar').toggleClass('d-none d-md-block');
    });
});
