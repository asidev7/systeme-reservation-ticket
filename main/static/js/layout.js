$(document).ready(function() {
	$('#ville').on('input', function() {
		var input = $(this).val();
		$.ajax({
			url: '/villes/?ville=' + input,
			type: 'get',
			dataType: 'json',
			success: function(response) {
				$('#villes').empty();
				$('#villes').append('<option value="">-- Sélectionnez une ville --</option>');
				response.forEach(function(ville) {
					$('#villes').append('<option value="' + ville + '">' + ville + '</option>');
				});
			},
			error: function(response) {
				alert('Erreur de chargement des villes');
			}
		});
	});
});
