$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				name : $('#nameInput').val(),
				password : $('#passwordInput').val()
			},
			type : 'POST',
			url : '/api/v1/users'
		})
		.done(function(data) {

			if (data.code == 400) {
				$('#errorAlert').text("UserName or Password missing").show();
				$('#successAlert').hide();
			}
			if (data.code == 405) {
				$('#errorAlert').text("User Already exist").show();
				$('#successAlert').hide();
			}
			if(data.code == 201) {
				$('#successAlert').text("Registration Successful").show();
				$('#errorAlert').hide();
			}

		});

		event.preventDefault();

	});

});