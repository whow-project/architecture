function dagRun(){
	$(".dagrun").on("click", function(e){
		e.preventDefault();
		dagId = $(this).attr("dag_id");
		configId = $(this).attr("config_id");
		console.log("DAG RUN triggered for DAG ID " + dagId + " and config ID " + configId);
		
		$.ajax({
			url: "./dag-run/api/" + dagId,
			method: 'GET',
			type: "GET",
			data: {"config_id": configId},
			//data: $(this),
			//contentType: 'multipart/form-data',
			contentType: false,
			cache: false,
			processData: true,
			success: function(data){
				console.log('DAG runned');
				window.location.href = "./dag-configs/api/" + dagId;
			},
			error: function(data){
				$('.portfolio').append('<p>An error occurred while executing the DAG.</p>')
			}
		});
	});

}

function dagStatus(){
	
	
	$.ajax({
		url: "./dag-status/api/" + $("#dag-configs").attr("dag_id"),
		method: 'GET',
		type: "GET",
		dataType: "json",
		success: function(data){
			if(data.status == "running"){
				$("i", $("#dagstatus")).removeClass("red")
				$("i", $("#dagstatus")).addClass("green")
			} 
			else {
				$("i", $("#dagstatus")).addClass("red")
				$("i", $("#dagstatus")).removeClass("green")
			}
		},
		error: function(data){
			$('.portfolio').append('<p>An error occurred while getting the DAG status.</p>')
		}
	});
	
	
	$("#dagstatus").on("click", function(e){
		e.preventDefault();
		dagId = $(this).attr("dag_id");
		configId = $(this).attr("config_id");
		console.log("DAG RUN triggered for DAG ID " + dagId + " and config ID " + configId);
		
		$.ajax({
			url: "./dag-run/api/" + dagId,
			method: 'GET',
			type: "GET",
			data: {"config_id": configId},
			//data: $(this),
			//contentType: 'multipart/form-data',
			contentType: false,
			cache: false,
			processData: true,
			success: function(data){
				console.log('DAG runned');
				window.location.href = "./dag-configs/api/" + dagId;
			},
			error: function(data){
				$('.portfolio').append('<p>An error occurred while creating the DAG.</p>')
			}
		});
	});

}

function dagConfigure(){
	$(".dagconfigure").on("click", function(e){
		dagId = $(this).attr("dag_id");
		window.location.href = "./dag-config/api/" + dagId;
	});

}

function addConfigurationButtons(){
	
	$("input[name='triplification-graph-id']").on("keydown", graphIDManagement);
	
	$(".add-dataset").on("click", function(e){
		
		content = '<div class="distribution group">'
				  + '<div class="input-group mb-3">'
	 			  + '<div class="input-group-prepend">'
	   			  + '<span class="input-group-text">Data file ID</span>'
	 			  + '</div>'
	 			  + '<input type="text" name="ingestion-data-file-id" placeholder="Some-ID" class="form-control" aria-label="Data file ID" />'
				  + '</div>'
				  + '<div class="input-group mb-3">'
 				  + '<div class="input-group-prepend">'
				  + '<span class="input-group-text">Data file ID</span>'
 				  + '</div>'
				  + '<select class="custom-select" name="ingestion-data-file-type">'
				  + '<option selected>Choose...</option>'
				  + '<option value="text/csv">CSV</option>'
 				  + '<option value="text/tab-separated-values">TSV</option>'
 				  + '<option value="application/json">JSON</option>'
 				  + '<option value="application/xml">XML</option>'
 				  + '</select>'
				  + '</div>'
				  + '<div class="input-group mb-3">'
 				  + '<div class="input-group-prepend">'
   				  + '<span class="input-group-text">Access URL</span>'
 				  + '</div>'
 				  + '<input type="text" name="ingestion-data-file-url" placeholder="https://someurl.foo" class="form-control" aria-label="Data file Access URL" />'
				  + '</div>'
				  + '</div>'
		
		
		$(this).before(content);
		
		distros = $(".distribution");
		
		if(distros.length > 1){
			$('.remove-dataset').show();
		}
		else {
			$('.remove-dataset').hide();
		}
		console.log(distros);
	});
	
	$(".remove-dataset").on("click", function(e){
		distros = $(".distribution");
		
		if(distros.length == 2){
			$('.remove-dataset').hide();
		}
		
		distro = distros[distros.length-1];
		$(distro).remove(); 
		
	});
	
	$(".remove-dataset").hide();
	
	$(".add-graph").on("click", function(e){
		
		content = '<div class="graph group">'
				  + '<div class="input-group mb-3">'
				  + '<div class="input-group-prepend">'
				  + '<span class="input-group-text">Graph ID</span>'
				  + '</div>'
				  + '<input type="text" name="triplification-graph-id" placeholder="Some-ID" class="form-control" aria-label="Graph ID" required />'
				  + '</div>'
				  + '<div class="rml group">'
				  + '<div class="input-group mb-3">'
				  + '<div class="input-group-prepend">'
				  + '<span class="input-group-text">RML descriptor</span>'
				  + '</div>'
				  + '<input type="text" name="triplification-rml" placeholder="http://someuri.foo" class="form-control" aria-label="RML ID" required />'
				  + '</div>'
				  + '</div>'
				  + '<button type="button" class="btn btn-success add-rml">+</button>'
				  + '<button type="button" class="btn btn-danger remove-rml">-</button>'
				  + '</div>'
		
		
		$(this).before(content);
		
		graphIDs = $("input[name='triplification-graph-id']")
		
		$(graphIDs[graphIDs.length-1]).attr("id", "triplification-graph-id-" + (graphIDs.length-1));
		$(graphIDs[graphIDs.length-1]).on("keydown", graphIDManagement);
		
		addRMLButtons = $('.add-rml');
		addRMLButton = addRMLButtons[addRMLButtons.length-1];
		$(addRMLButton).on("click", addRML) ;
		
		removeRMLButtons = $('.remove-rml');
		removeRMLButton = removeRMLButtons[removeRMLButtons.length-1];
		$(removeRMLButton).on("click", removeRML) ;
		$(removeRMLButton).hide();
		
		graphs = $(".graph");
		
		if(graphs.length > 1){
			$('.remove-graph').show();
		}
		else {
			$('.remove-graph').hide();
		}
		
	});
	
	$(".remove-graph").on("click", function(e){
		graphs = $(".graph");
		
		if(graphs.length == 2){
			$('.remove-graph').hide();
		}
		
		graph = graphs[graphs.length-1];
		graphId = $("input[name='triplification-graph-id']", graph).attr("id");
		
		options = $("select[name='metadating-graph-id'] option[for='" + graphId +"']");
		$(options).remove();
		
		$(graph).remove(); 
		
		
		
	});
	
	$(".remove-graph").hide();
	
	$(".add-rml").on("click", addRML);
	
	$(".remove-rml").on("click", removeRML);
	
	$(".remove-rml").hide();
	
	
	$(".add-metadating").on("click", function(e){
		
		content = '<div class="metadating group">'
				  + '<div class="input-group mb-3">'
				  + '<div class="input-group-prepend">'
				  + '<span class="input-group-text">Graph ID</span>'
				  + '</div>'
				  + '<select class="custom-select" name="metadating-graph-id" required>'
				  + '<option selected>Choose...</option>'
				  + '</select>'
				  + '</div>'
				  + '<div class="input-group mb-3">'
				  + '<div class="input-group-prepend">'
				  + '<span class="input-group-text">Dataset ID</span>'
				  + '</div>'
				  + '<input type="text" name="metadating-dataset-id" placeholder="http://someuri.foo/dataset_id" class="form-control" aria-label="Dataset ID" required />'
				  + '</div>'
				  + '<div class="input-group mb-3">'
				  + '<div class="input-group-prepend">'
				  + '<span class="input-group-text">Distribution ID</span>'
				  + '</div>'
				  + '<input type="text" name="metadating-distribution-id" placeholder="http://someuri.foo/distribu_id" class="form-control" aria-label="Distribution ID" required />'
				  + '</div>'
				  + '<div class="input-group mb-3">'
				  + '<div class="input-group-prepend">'
				  + '<span class="input-group-text">INI Configuration file</span>'
				  + '</div>'
				  + '<input type="text" name="metadating-config" placeholder="http://someuri.foo/ini_props" class="form-control" aria-label="Metadata INI Config" required />'
				  + '</div>'
				  + '</div>'
		
		
		$(this).before(content);
		
		metas = $(".metadating");
		
		if(metas.length > 1){
			$(".remove-metadating").show();
			
			selects = $("select[name='metadating-graph-id']")
			options = $("option", selects[0])
			
			select = selects[selects.length-1]
			$(options).each(function(index){
				if(index > 0){
					$(select).append('<option for="' + $(this).attr("for") + '" value="' + $(this).val() + '">' + $(this).text() + '</option>');
				}
			});
			
		}
		else {
			$('.remove-metadating').hide();
		}
	});
	
	$(".remove-metadating").on("click", function(e){
		metas = $(".metadating");
		
		if(metas.length == 2){
			$('.remove-metadating').hide();
		}
		
		meta = metas[metas.length-1];
		$(meta).remove();
		
	});
	
	$(".switch-option").on("click", function(e){
		if($("#upload").is(":visible") && $("#edit").is(":hidden")){
			$("#upload").hide();
			$("#edit").show();
			$(this).text("Upload configuration")
			
			$(".switch-dark").before($(".switch-option").parent())
		}
		else {
			$("#upload").show();
			$("#edit").hide();
			$(this).text("Edit configuration")
			
			$(".switch-dark").after($(".switch-option").parent())
		}
		
	});
	
	$(".remove-metadating").hide();
	
	if($("#upload").length == 1) {
		$("#upload").show();
		$("#edit").hide();
	}
	else {
		$("#edit").show();
	}
	
	$("#upload-json").on("click", function(e){
		e.preventDefault();
		jsonFile = $($("input[name='json']", $(this).parent())[0]).prop('files')[0]
		fr = new FileReader();
		
		fr.addEventListener('load', (event) => {
    		result = event.target.result;
  		
			$.ajax({
				url: $("#config-form").attr('action'),
				method: 'POST',
				type: "POST",
				data: fr.result,
				//data: $(this),
				contentType: 'application/json',
				cache: false,
				processData: false,
				success: function(data){
					console.log('DAG Config created');
					window.location.href = "./dag-configs/api/" + $("#dag_id").attr("title");;
				},
				error: function(data){
					$('.portfolio').append('<p>An error occurred while creating the DAG configuration.</p>')
				}
			});
		});
		
		
		fr.readAsText(jsonFile)
		
		
		
		
		
	});
	
	$("#load-configuration").on("click", function(e){
		
		jsonObj = {}
		
		boundServices = {}
		$(".subsection").each(function(index){
			id = $(this).attr("id");
			
			if(id=="metadata-section"){
				metadata = {}
				metadata["id"] = $("input[name='id']", this).val();
				metadata["name"] = $("input[name='name']", this).val();
				metadata["description"] = $("textarea[name='description']", this).val();
				jsonObj["metadata"] = metadata;
			}
			else if(id=="ingestion-section"){
				ingestion = {};
				ingestion["endpoint"] = $("input[name='ingestion-endpoint']", this).val();
				
				ingestionData = {}
				ingestionData["title"] = $("input[name='ingestion-dataset-title']", this).val();
				ingestionData["description"] = $("textarea[name='ingestion-dataset-description']", this).val();
				ingestionData["store"] = true;
				
				distributions = [];
				
				$(".distribution").each(function(i){
					distro = {}
					distro["id"] = $("input[name='ingestion-data-file-id']", this).val();
					distro["mimetype"] = $("select[name='ingestion-data-file-type']", this).val();
					distro["accessURL"] = $("input[name='ingestion-data-file-url']", this).val();
					
					distributions.push(distro);
				});
				
				ingestionData["distributions"] = distributions;
				
				ingestion["data"] = ingestionData 
				
				boundServices["https://w3id.org/whow/onto/flow/ingestion"] = ingestion;
			} 
			else if(id=="preprocessing-section"){
				preprocessing = {};
				preprocessing["endpoint"] = $("input[name='preprocessing-endpoint']", this).val();
				
				preprocessingData = {};
				
				ids = [];
				$(".distribution").each(function(i){
					ids.push($("input[name='ingestion-data-file-id']", this).val());
				});
				
				preprocessingData["ids"] = ids;
				preprocessing["data"] = preprocessingData;
				
				boundServices["https://w3id.org/whow/onto/flow/preprocessing"] = preprocessing;
			} 
			else if(id=="triplification-section"){
				triplification = {};
				triplification["endpoint"] = $("input[name='triplification-endpoint']", this).val();
				
				triplificationData = {};
				
				graphs = [];
				$(".graph", this).each(function(i){
					graph = {};
					graph["id"] = $("input[name='triplification-graph-id']", this).val();
					
					rmls = [];
					$(".rml", this).each(function(k){
						rml = {"id": $("input[name='triplification-rml']", this).val()};
						rmls.push(rml);
					});
					graph["rmls"] = rmls;
					
					graphs.push(graph)
				});
				
				triplificationData["graphs"] = graphs;
				triplification["data"] = triplificationData;
				
				boundServices["https://w3id.org/whow/onto/flow/mapping"] = triplification;
			} 
			else if(id=="metadating-section"){
				metadating = {};
				metadating["endpoint"] = $("input[name='metadating-endpoint']", this).val();
				
				metadatingData = {};
				
				metas = [];
				$(".metadating", this).each(function(i){
					meta = {};
					meta["id"] = $("select[name='metadating-graph-id']", this).val();
					meta["dataset_id"] = $("input[name='metadating-dataset-id']", this).val();
					meta["distribution_id"] = $("input[name='metadating-distribution-id']", this).val();
					meta["configuration"] = $("input[name='metadating-config']", this).val();
					
					
					metas.push(meta)
				});
				
				metadatingData["meta"] = metas;
				metadating["data"] = metadatingData;
				
				boundServices["https://w3id.org/whow/onto/flow/metadating"] = metadating;
			}
			else if(id=="reasoning-section"){
				reasoning = {};
				reasoning["endpoint"] = $("input[name='reasoning-endpoint']", this).val();
				
				reasoningData = {};
				
				graphs = [];
				$(".reasoning", this).each(function(i){
					graph = {};
					graph["id"] = $("select[name='reasoning-graph-id']", this).val();
					
					ontologies = [];
					
					$(".ontology", this).each(function(k){
						ontology = {};
						ontology["id"] = $("input[name='ontology-uri']", this).val();
						
						ontologies.push(ontology);
					});
					graph["ontologies"] = ontologies;
					
					graphs.push(graph)
				});
				
				reasoningData["reasoning"] = graphs;
				reasoning["data"] = reasoningData;
				
				boundServices["https://w3id.org/whow/onto/flow/reasoning"] = reasoning;
			}
			else if(id=="validation-section"){
				validation = {};
				validation["endpoint"] = $("input[name='validation-endpoint']", this).val();
				
				boundServices["https://w3id.org/whow/onto/flow/validation"] = validation;
			}
			else if(id=="storing-section"){
				storing = {};
				storing["endpoint"] = $("input[name='storing-endpoint']", this).val();
				
				boundServices["https://w3id.org/whow/onto/flow/storing"] = storing;
			}
		});
		
		jsonObj["bound_services"] = boundServices;
		
		console.log(jsonObj)
		
		dagId = $("#dag_id").attr("title");
		
		$.ajax({
			url: $("#config-form").attr('action'),
			method: 'POST',
			type: "POST",
			data: JSON.stringify(jsonObj),
			//data: $(this),
			contentType: 'application/json',
			cache: false,
			processData: false,
			success: function(data){
				console.log('DAG Config created');
				window.location.href = "./dag-configs/api/" + dagId;
			},
			error: function(data){
				$('.portfolio').append('<p>An error occurred while creating the DAG configuration.</p>')
			}
		});
		
	});
	
	$("#exit-configuration").on("click", function(e){
		window.location.href = "./dag-configs/api/" + $("#dag_id").attr("title");
	});
	$(".edit-configuration").on("click", function(e){
		window.location.href = "./dag-config/api/" + $("#dag_id").attr("title") + "?config_id=" + $("input[name='id']", $("#metadata")).val() + "&mode=edit";
	});
}

function addRML(e){
		
	content = '<div class="rml group">'
			  + '<div class="input-group mb-3">'
			  + '<div class="input-group-prepend">'
			  + '<span class="input-group-text">RML descriptor</span>'
			  + '</div>'
			  + '<input type="text" name="triplification-rml" placeholder="http://someuri.foo" class="form-control" aria-label="RML ID" required />'
			  + '</div>'
			  + '</div>'
	
	
	$(this).before(content);
	
	rmls = $(".rml", $(this).parent());
	
	if(rmls.length > 1){
		$(".remove-rml", $(this).parent()).show();
	}
	else {
		$(".remove-rml", $(this).parent()).hide();
	}
	
}

function removeRML(e){
	rmls = $(".rml", $(this).parent());
	
	if(rmls.length == 2){
		$(".remove-rml", $(this).parent()).hide();
	}
	
	rml = rmls[rmls.length-1];
	$(rml).remove(); 
	
}

function graphIDManagement(e) {
	if (e.keyCode == 13) {
		if(e.keyCode == 13){
			graphID = $(this).val();
			id = $(this).attr("id")
			options = $("select[name='metadating-graph-id'] option[for='" + id + "']");
			
			if(options.length == 0){
				$("select[name='metadating-graph-id']").append(
					$('<option for="' + id + '" value="' + graphID +'">' + graphID + '</option>'))
			}
			else{
				opt = options[0];
				$(opt).val(graphID);
				$(opt).text(graphID);
			}
       }
    }
};


$(document).ready( function (){
	window.setInterval(function(){
		dagStatus();	
	}, 5000);
	dagRun();
	dagConfigure();
	addConfigurationButtons();
});