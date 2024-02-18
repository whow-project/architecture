function createDAG(){
	$("form").submit(function(e){
		e.preventDefault();
		
		var filename = $("form input[type='file']").val();
		var extension = filename.replace(/^.*\./, '');
		
		var contentType = "";
		if(extension == "ttl"){
			contentType = "text/turtle";
		}
		else if(extension == "rdf"){
			contentType = "application/rdf+xml";
		}
		else if(extension == "json" || extension == "json-ld"){
			contentType = "application/json-ld";
		}
		else if(extension == "nt"){
			contentType = "application/n-triples";
		}
		else{
			contentType = "text/turtle";
		}
		
		console.log('content type ' + contentType)
		formData = new FormData();
		file = $("form input[type='file']")[0].files[0];
		newFile = new File([file], file.name, {type: contentType});
		formData.append("graph", newFile, file.name)
		
		
		$.ajax({
			url: $(this).attr('action'),
			method: 'POST',
			type: "POST",
			data: formData,
			//data: $(this),
			//contentType: 'multipart/form-data',
			contentType: false,
			cache: false,
			processData: false,
			success: function(data){
				console.log('DAG created');
				window.location.href = "./dagstore/api/dags";
			},
			error: function(data){
				$('.portfolio').append('<p>An error occurred while creating the DAG.</p>')
			}
		});
	});

}



$(document).ready( function (){
	createDAG()
	});