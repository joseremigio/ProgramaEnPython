$(document).ready(function(){

  //Formulario inicio index
  if($("#suscribete").length==1){
    //Mostrar tooltip
    $('[data-toggle="tooltip"]').tooltip();
  }
  //Formulario fin index

  $("#operacion").click(function() {
    var enviar = $("#enviar").val();
    var tipoMonedaEnviar = $("#tipoMonedaEnviar").text();
    var tipoMonedaRecibir = $("#tipoMonedaRecibir").text();
    var url = "/operacion"; 
    location.href=url+"/"+enviar+'-'+tipoMonedaEnviar+'-'+tipoMonedaRecibir;
  });

  //calcular dolares
  $("#enviar").change(function() {
  	enviarMonto ();
    if($("#formularioOperacion").length==1){
      getDataCuentasEmpresa();
    }
  });

  //calcular soles
  $("#recibir").change(function() {
	  recibirMonto ();
    if($("#formularioOperacion").length==1){
      getDataCuentasEmpresa();
    }
  });

  //Re calcular cuando cambias el tipo de cambio
  $("#valor_compra").change(function() {
    $("#enviar").val(100);
    $("#cambio").click();
  });

  $("#valor_venta").change(function() {
    $("#enviar").val(100);
    $("#cambio").click();
  });


  //actualizar monto 
  $("#cambio").click(function() {
  	var tipoMonedaEnviar = $("#tipoMonedaEnviar").text();
  	var tipoMonedaRecibir = $("#tipoMonedaRecibir").text();
  	$("#tipoMonedaEnviar").text(tipoMonedaRecibir);
  	$("#tipoMonedaRecibir").text(tipoMonedaEnviar);
  	enviarMonto ();
  	$("#cambioValor").val(tipoMonedaRecibir);
  });

  function enviarMonto (){
  	var enviarValor = $("#enviar").val();
  	var tipoMonedaEnviar = $("#tipoMonedaEnviar").text();
	  //calcular monto a recibir
  	var recibirValor = calcularMontoEnviar(enviarValor,tipoMonedaEnviar);
  	$("#recibir").val(recibirValor);
    vueltoCompraVenta(enviarValor, tipoMonedaEnviar);

  }

  function vueltoCompraVenta(enviarValor, tipoMoneda) {
     //calcular vuelto
  	 var CancelaCon     =  $("#CancelaCon").val();
     var vuelto         = parseFloat(CancelaCon) - parseFloat(enviarValor);
     document.getElementById('vuelto').value       = vuelto + " " + tipoMoneda;
     document.getElementById('vuelto').innerHTML   = vuelto + " " + tipoMoneda;
  }

  function cambiarCuentaDestino (){
    //seleccionamos la cuenta de la moneda a recibir - form operacion
    var tipoMonedaRecibir = $("#tipoMonedaRecibir").text();
    if ($("#numero_cuenta option").length!=0){
      var numero_cuentaOption = $("#numero_cuenta option")[0].label;
      if (numero_cuentaOption.split("-")[1]==tipoMonedaRecibir){
        $("#numero_cuenta").val($("#numero_cuenta option")[0].value);
      }
      else {
        $("#numero_cuenta").val($("#numero_cuenta option")[1].value);
      }
    }
  }



  function recibirMonto (){
  	var recibirValor = $("#recibir").val();
  	//obtener tipo de cambio
  	var tipoMonedaRecibir = $("#tipoMonedaRecibir").text();
	//calcular monto a recibir
  	var enviarValor = calcularMontoRecibir(recibirValor,tipoMonedaRecibir);
  	$("#enviar").val(enviarValor);
  	vueltoCompraVenta(enviarValor, "")
  }

  function calcularMontoEnviar(enviar, tipoMoneda) {
  	var recibirValor=0;
  	if (tipoMoneda==="Soles"){
  		//obtener tipo de cambio
  		var tipoCambio = $("#valor_venta").val();
        $("#tipoCambio").text(tipoCambio);
	  	recibirValor = (enviar / tipoCambio).toFixed(3);
	  	document.getElementById('valor_venta').style.fontWeight = 'bold';
	  	$("#valor_venta").addClass("bg-primary text-white");
        document.getElementById('valor_compra').style.fontWeight = 'normal';
        $("#valor_compra").removeClass("bg-primary text-white");
  	}
  	if (tipoMoneda==="Dolares"){
  		//obtener tipo de cambio
  		var tipoCambio = $("#valor_compra").val();
        $("#tipoCambio").text(tipoCambio);
	  	recibirValor = (enviar * tipoCambio).toFixed(3);
        document.getElementById('valor_compra').style.fontWeight = 'bold';
        $("#valor_compra").addClass("bg-primary text-white");
        document.getElementById('valor_venta').style.fontWeight = 'normal';
        $("#valor_venta").removeClass("bg-primary text-white");
  	}

  	return recibirValor;
  }

  function calcularMontoRecibir(recibir, tipoMoneda) {
    var recibirValor=0;
    if (tipoMoneda==="Soles"){
      //obtener tipo de cambio
      var tipoCambio = $("#valor_compra").val();
      $("#tipoCambio").text(tipoCambio);
      recibirValor = (recibir / tipoCambio).toFixed(2);
    }
    if (tipoMoneda==="Dolares"){
      //obtener tipo de cambio
      var tipoCambio = $("#valor_venta").val();
      $("#tipoCambio").text(tipoCambio);
      recibirValor = (recibir * tipoCambio).toFixed(2);
    }

    return recibirValor;
  }

  //Mover el boton de cambio en formulario compra y venta
 $(".loading-icon").click(function() {
    var icon = $(this).find("i");
    if (!icon.hasClass("spin-once")) {
      icon.addClass("spin-once").on("animationend", function() {
        icon.removeClass("spin-once");
      });
    }
  });

  $("#banco_id").change(function() {
    $("#banco_dolar").val($("#banco_id option:selected").text());
  });

  $("#TipoOperacionId").change(function() {
        if ($('select[name="TipoOperacionId"] option:selected').text() =="Pago de Servicio (DEPOSITO)"){
            $("#Comentario").val("PAGO DE SERVICIO");
            $('#Comentario').prop('readonly', true);
        }
        else {
            $('#Comentario').prop('readonly', false);
            $("#Comentario").val("");
        }

        if ($("#TipoOperacionId").val()==2){
            $("#PagoBancoId").prop("disabled", false);
            //document.getElementById("BancoReceptorId").removeAttribute("disabled");
            $('#MontoBanco').prop('readonly', false);
        }
        else {
            $("#PagoBancoId").prop("disabled", true);
            //document.getElementById("BancoReceptorId").setAttribute("disabled", "disabled");
            $('#MontoBanco').prop('readonly', true);
            $('#MontoBanco').val(0);
            calcularVuelto();
        }
  });

  function getDataCuentas(){
    $.ajax({
      type: "GET",
      url: location.origin+'/cuentasPorBanco/'+ $("#banco_id").val(), 
      dataType: "json",
      success: function(data){
        //limpiar opciones
        $("#numero_cuenta").empty(); 
        
        //no tiene cuenta registradas
        var noTieneCuenta = false;
        var alertaUsuarioSinCuenta = "hidden";
        if (data.elements.length===0){
          $("#numero_cuenta").append('<option value="">Sin Cuentas registradas</option>');
          noTieneCuenta=true;
          alertaUsuarioSinCuenta = "visible";
        }
        else {
          $.each(data.elements,function(key, cuenta){
            var selected ='';
            var moneda = getConvertirTextoMoneda(cuenta.tipoCuenta);
            if($("#tipoMonedaRecibir").text()==moneda){
              selected ='selected';
            }
           
            $("#numero_cuenta").append('<option '+selected+' value='+cuenta.cuentaId+'>'+cuenta.numeroCuenta+'-'+ moneda+'</option>');
          });
          getDataCuentasEmpresa();
        }

        $("#alertaUsuarioSinCuenta").css("visibility", alertaUsuarioSinCuenta);
        $("#btn-siguiente-operacion").attr("disabled", noTieneCuenta);

      },
      error: function(data) {
        alert('error');
      }
    });
  }
  //convertir texto de moneda
  function getConvertirTextoMoneda(moneda){
    if (moneda==="SOLES"){
      moneda = "Soles";
    }
    if (moneda==="DOLARES AMERICANOS"){
      moneda = "Dolares";
    }
    return moneda;
  } 
  //cargar cuentas de la casa de cambio
   function getDataCuentasEmpresa(){
    $.ajax({
      type: "GET",
      url: location.origin+'/cuentasEmpresa/'+ $("#banco_id").val(), 
      dataType: "json",
      success: function(data){
        if (data.elements.length===0){
          $("#alertaCasaCambioSinCuenta").css("visibility", "visible");
          $("#btn-siguiente-operacion").attr("disabled", true);
        }
        else
        {
          $.each(data.elements,function(key, cuenta){
            moneda = getConvertirTextoMoneda(cuenta.tipoCuenta);
            if($("#tipoMonedaRecibir").text()==moneda){
              //validamos si la casa de cambio cuenta con el monto minimo
              if(cuenta.monto>=Number($("#recibir").val())){
                $("#numeroCuentaBancoEmpresa").text(cuenta.numeroCuenta);
                $("#alertaCasaCambioSinFondo").css("visibility", "hidden");
              }
              else {
                $("#alertaCasaCambioSinFondo").css("visibility", "visible");
                $("#numeroCuentaBancoEmpresa").text("000000000000000000");
              }
              $("#cuenta_destino_id").val(cuenta.cuentaId);
            }
          });

          $("#alertaCasaCambioSinCuenta").css("visibility", "hidden");
          $("#btn-siguiente-operacion").attr("disabled", false);
        }
        
      },
      error: function(data) {
        alert('error');
      }
    });
  }

  //Actualizar datos de 2/3 TRANSFIERE A NUESTRA CUENTA
  function actualizarDatosBancoDestino(){
    var banco_id = $("#banco_id option:selected").text();
    $("#nombreBancoDestino").text(banco_id);
    var tipoMonedaRecibir = $("#tipoMonedaRecibir").text();
    $("#tipoCuentaBancoDestino").text(tipoMonedaRecibir);
  }

  //Formulario Operacion
  if($("#formularioOperacion").length==1){
    
    getDataCuentas();
    actualizarDatosBancoDestino();
    enviarMonto ();
    cambiarCuentaDestino();
    
    $("#banco_id").change(function() {
      getDataCuentas();
      actualizarDatosBancoDestino();
    });

    //boton actualizar monto - form operacion
    $("#cambioOperacion").click(function() {
      var tipoMonedaEnviar = $("#tipoMonedaEnviar").text();
      var tipoMonedaRecibir = $("#tipoMonedaRecibir").text();
      $("#tipoMonedaEnviar").text(tipoMonedaRecibir);
      $("#tipoMonedaRecibir").text(tipoMonedaEnviar);
      actualizarDatosBancoDestino();
      getDataCuentasEmpresa();
      enviarMonto ();
      cambiarCuentaDestino();
    });

    $("#numero_cuenta").change(function(){
      var tipoMonedaEnviar = $("#tipoMonedaEnviar").text();
      var tipoMonedaRecibir = $("#tipoMonedaRecibir").text();
      var tipoMonedaComboCuentaSelect = $("#numero_cuenta option:selected").text().split("-")[1];
      if(tipoMonedaComboCuentaSelect===tipoMonedaRecibir){

      }
      else{
         $("#tipoMonedaEnviar").text(tipoMonedaRecibir);
         $("#tipoMonedaRecibir").text(tipoMonedaEnviar);

      }
      actualizarDatosBancoDestino();
      getDataCuentasEmpresa();
      enviarMonto ();
    });

  }
  //fin form operacion

  //Formulario formularioEmpresaListado
  if($("#formularioEmpresaListado").length==1){
    
     var table = $('#example').DataTable({
        columnDefs: [{
            orderable: true,
            targets: [1,2,3]
        }],
        "scrollX": true
    });

    $("#cliente_ids").val(table.$('input, select').serialize());

    $(".cliente_id").change(function() { 
      $("#cliente_ids").val(table.$('input, select').serialize());
    });
  }
  //fin formularioEmpresaListado

  //Formulario transferir de agente, validar transferencia entre cajas de s./ y $
  if($("#transferirForm").length==1){
      $('#BancoDestinoId').on('change', function() {
          if ($("#BancoOrigenId  option:selected").val()==$("#BancoDestinoId  option:selected").val()){
                $("#btnRegistra").attr("disabled", true);
                alert( "El Banco Origen y Destino no pueden ser iguales.");
          }
          else if ($("#BancoOrigenId option:selected").text().includes("SOLES") && $("#BancoDestinoId option:selected").text().includes("SOLES")) { //Si la opcion selecciona contiene la palabra SOLES
                $("#btnRegistra").attr("disabled", false);
                $('#TipoMonedaDolar').prop('checked', false);
                $('#TipoMonedaSol').prop('checked', true);
          }
          else if ($("#BancoOrigenId option:selected").text().includes("DOLARES") && $("#BancoDestinoId option:selected").text().includes("DOLARES")) { //Si la opcion selecciona contiene la palabra DOLARES
                $("#btnRegistra").attr("disabled", false);
                $('#TipoMonedaDolar').prop('checked', true);
                $('#TipoMonedaSol').prop('checked', false);
          }
          else if ($("#BancoOrigenId option:selected").text().includes("DOLARES") || $("#BancoDestinoId option:selected").text().includes("DOLARES")){
                $("#btnRegistra").attr("disabled", true);
                alert( "Debe de seleccionar ambas cajas con el mismo tipo de moneda.");
          }
          else if ($("#BancoOrigenId option:selected").text().includes("SOLES") || $("#BancoDestinoId option:selected").text().includes("SOLES")){
                $("#btnRegistra").attr("disabled", true);
                alert( "Debe de seleccionar ambas cajas con el mismo tipo de moneda.");
          }
          else {
                $('#TipoMonedaDolar').prop('checked', false);
                $('#TipoMonedaSol').prop('checked', true);
                $("#btnRegistra").attr("disabled", false);
          }
       });
  }
   //Formulario de transferencia transferirWu
  if($("#transferirWuForm").length==1){
        $('#BancoOrigenId').on('change', function() {
          if ($("#BancoOrigenId option:selected").text().includes("SOLES")){
            $("#BancoDestinoId").val("22"); //22=EFECTIVO WU (Caja Principal) - SOLES
          }
          if ($("#BancoOrigenId option:selected").text().includes("DOLARES")){
            $("#BancoDestinoId").val("23"); //22=EFECTIVO WU (Caja Principal) - DOLARES
          }
        });
        $('#BancoDestinoId').on('change', function() {
          if ($("#BancoOrigenId option:selected").text().includes("DOLARES") && $("#BancoDestinoId option:selected").text().includes("SOLES")){
             $("#btnRegistra").attr("disabled", true);
             alert( "Debe de seleccionar ambas cajas con el mismo tipo de moneda.");
          }
          else if ($("#BancoOrigenId option:selected").text().includes("SOLES") && $("#BancoDestinoId option:selected").text().includes("DOLARES")){
             $("#btnRegistra").attr("disabled", true);
             alert( "Debe de seleccionar ambas cajas con el mismo tipo de moneda.");
          }
          else {
             $("#btnRegistra").attr("disabled", false);
          }
        });
   }

   //Formulario remesas wester
   $('#WesterBancoId').on('change', function() {
        if ($("#WesterTipoOperacionId option:selected").text().includes("RETIRO")){
                if ($("#WesterBancoId option:selected").text().includes("SOLES")){
                    $('#remesaSolRetiro').show();
                    $("#remesaDolarRetiro").hide();
                }
                else {
                    $('#remesaDolarRetiro').show();
                    $("#remesaDolarDeposito").hide();
                }
        }
        else {

        }

   });

   $('#remesaDolarRetiroTotal').on('change', function() {
        var remesaDolarRetiroDolarDiferencia =  $("#remesaDolarRetiroTotal")[0].value - $("#remesaDolarRetiroMontoDolar")[0].value;
        var remesaDolarRetiroMontoSol = remesaDolarRetiroDolarDiferencia * $("#remesaDolarRetiroTipoCambio")[0].value;
        $('#remesaDolarRetiroMontoSol').val(remesaDolarRetiroMontoSol);
   });

   $('#remesaDolarRetiroMontoDolar').on('change', function() {
        var remesaDolarRetiroDolarDiferencia =  $("#remesaDolarRetiroTotal")[0].value - $("#remesaDolarRetiroMontoDolar")[0].value;
        var remesaDolarRetiroMontoSol = remesaDolarRetiroDolarDiferencia * $("#remesaDolarRetiroTipoCambio")[0].value;
        $('#remesaDolarRetiroMontoSol').val(remesaDolarRetiroMontoSol);
   });

   $('#tipoOperacionIdDolar').on('change', function() {
        document.getElementById('montoDolarWu').value = 0;
        document.getElementById('montoDolarCaja').value =0;
        document.getElementById('comisionSol').value =0;
        document.getElementById('tipoCambioCompra').style.fontWeight = 'normal';
        document.getElementById('tipoCambioVenta').style.fontWeight = 'normal';
        $("#tipoCambioCompra").removeClass("bg-secondary text-white");
        $("#tipoCambioVenta").removeClass("bg-secondary text-white");
   });

  //Formulario de Cierre de Caja Wu
  if($("#cierreFormWu").length==1){

    //Actualizar saldo de tabla resumen
    //EFECTIVO WU (Caja Principal) - SOLES
    $('#bancoid_22').text($("#montofinalreal_22").val());
    //EFECTIVO WU (Caja Principal) - DOLARES
    $('#bancoid_23').text($("#montofinalreal_23").val());
    //BCP - SOLES
    $('#bancoid_26').text($("#montofinalreal_26").val());
    //BCP - DOLARES
    $('#bancoid_27').text($("#montofinalreal_27").val());
    //SCOTIABANK - SOLES
    $('#bancoid_28').text($("#montofinalreal_28").val());
    //SCOTIABANK - DOLARES
    $('#bancoid_29').text($("#montofinalreal_29").val());
    //WESTER UNION - REMESA - SOLES (HOY)
    $('#bancoid_30').text($("#montofinalreal_30").val());
    //WESTER UNION - REMESA - DOLARES (HOY)
    $('#bancoid_31').text($("#montofinalreal_31").val());
    //WESTER UNION - REMESA - SOLES (AYER)
    $('#bancoid_32').text($("#montofinalreal_32").val());
    //WESTER UNION - REMESA - DOLARES (AYER)
    $('#bancoid_33').text($("#montofinalreal_33").val());
    //WESTER UNION - REMESA - SOLES (HACE 2 DÍAS)
    $('#bancoid_34').text($("#montofinalreal_34").val());
    //WESTER UNION - REMESA - DOLARES (HACE 2 DÍAS)
    $('#bancoid_35').text($("#montofinalreal_35").val());
    //WESTER UNION - REMESA - SOLES (HACE 3 DÍAS)
    $('#bancoid_36').text($("#montofinalreal_36").val());
    //WESTER UNION - REMESA - DOLARES (HACE 3 DÍAS)
    $('#bancoid_37').text($("#montofinalreal_37").val());
    //WESTER UNION - REMESA - DOLARES (HACE 4 DÍAS)
    $('#bancoid_38').text($("#montofinalreal_38").val());
    //WESTER UNION - REMESA - SOLES (HACE 4 DÍAS)
    $('#bancoid_39').text($("#montofinalreal_39").val());

    function calcularMontoIniciaYFinal () {
        //Obtener tipo de compra de hoy
        var tipoCompraDiaActual = parseFloat($("#tipoCompraDiaActual").val());
        //Calcular montofinalreal
        var totalSolesMontoFinalReal    = parseFloat($("#montofinalreal_22").val()) + parseFloat($("#montofinalreal_26").val()) + parseFloat($("#montofinalreal_28").val()) + parseFloat($("#montofinalreal_30").val()) +
                                parseFloat($("#montofinalreal_32").val()) + parseFloat($("#montofinalreal_34").val()) + parseFloat($("#montofinalreal_36").val()) + parseFloat($("#montofinalreal_38").val());
        $('#total_soles').text(totalSolesMontoFinalReal.toFixed(2));

        var totalDolaresMontoFinalReal  = parseFloat($("#montofinalreal_23").val()) + parseFloat($("#montofinalreal_27").val()) + parseFloat($("#montofinalreal_29").val()) + parseFloat($("#montofinalreal_31").val()) +
                                parseFloat($("#montofinalreal_33").val()) + parseFloat($("#montofinalreal_35").val()) + parseFloat($("#montofinalreal_37").val()) + parseFloat($("#montofinalreal_39").val());
        $('#total_dolares').text(totalDolaresMontoFinalReal.toFixed(2));

        var totalMontoFinalReal         = totalSolesMontoFinalReal + (totalDolaresMontoFinalReal*tipoCompraDiaActual);
        $('#totalMontoFinalReal').text(totalMontoFinalReal.toFixed(2));
        $('#totalMontoFinalReal2').text(totalMontoFinalReal.toFixed(2));

        //Calcular montoinicial
        var totalSolesMontoInicial      = parseFloat($("#montoinicial_22").val()) + parseFloat($("#montoinicial_26").val()) + parseFloat($("#montoinicial_28").val()) + parseFloat($("#montoinicial_30").val()) +
                                parseFloat($("#montoinicial_32").val()) + parseFloat($("#montoinicial_34").val()) + parseFloat($("#montoinicial_36").val()) + parseFloat($("#montoinicial_38").val());

        var totalDolaresMontoInicial    = parseFloat($("#montoinicial_23").val()) + parseFloat($("#montoinicial_27").val()) + parseFloat($("#montoinicial_29").val()) + parseFloat($("#montoinicial_31").val()) +
                                parseFloat($("#montoinicial_33").val()) + parseFloat($("#montoinicial_35").val()) + parseFloat($("#montoinicial_37").val()) + parseFloat($("#montoinicial_39").val());

        //Obtener tipo de compra de ayer
        var tipoCompraDiaAnterior       = parseFloat($("#tipoCompraDiaAnterior").val());

        var totalMontoInicial = totalSolesMontoInicial + (totalDolaresMontoInicial*tipoCompraDiaAnterior);
        $('#totalMontoInicial').text(totalMontoInicial.toFixed(2));
        $('#totalMontoInicial2').text(totalMontoInicial.toFixed(2));
        var ganancia = totalMontoFinalReal - totalMontoInicial;
        $('#ganancia').text(ganancia.toFixed(2));
    }

    calcularMontoIniciaYFinal();

    $('#tipoCompraDiaActual').on('change', function() {
      calcularMontoIniciaYFinal();
    });

    $("#tipoCompraDiaActual").keypress(function(){
      calcularMontoIniciaYFinal ();
    });

    $("#tipoCompraDiaActual").on("keydown", function(event) {
      calcularMontoIniciaYFinal ();
    });

    $("#tipoCompraDiaActual").on("keyup", function(event) {
      calcularMontoIniciaYFinal ();
    });

    $('#tipoCompraDiaAnterior').on('change', function() {
        calcularMontoIniciaYFinal();
    });

    $("#tipoCompraDiaAnterior").keypress(function(){
      calcularMontoIniciaYFinal ();
    });

    $("#tipoCompraDiaAnterior").on("keydown", function(event) {
      calcularMontoIniciaYFinal ();
    });

    $("#tipoCompraDiaAnterior").on("keyup", function(event) {
      calcularMontoIniciaYFinal ();
    });
  }


  $('#exampleModal').on('show.bs.modal', function (event) {
                  var button = $(event.relatedTarget) // Button that triggered the modal
                  var recipient = button.data('whatever') // Extract info from data-* attributes
                  // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
                  // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
                  var modal = $(this)
                  modal.find('.modal-title').text('New message to ' + recipient)
                  modal.find('.modal-body input').val(recipient)
  })

  //Formulario Nueva Operacion - Agente
  if($("#formRegistarOperacion").length==1){
    $("input").keypress(function(){
        calcularVuelto();
    });

     $("input").on("keydown", function(event) {
      calcularVuelto();
    });

    $("input").on("keyup", function(event) {
      calcularVuelto();
    });

    if (isNaN(document.getElementById('vuelto').value)) {
        var vuelto = 0;
        document.getElementById('vuelto').value       ="S/ "+ vuelto;
        document.getElementById('vuelto').innerHTML   ="S/ "+ vuelto;
    }

    // Obtén una referencia al formulario y al botón de envío
    var formulario = document.getElementById("formRegistarOperacion");
    var botonEnviar = document.getElementById("botonEnviar");

    // Agrega un controlador de eventos al formulario para manejar el envío
    formulario.addEventListener("submit", function (event) {
      event.preventDefault(); // Evita que el formulario se envíe de manera predeterminada
      // Realiza tus validaciones o acciones personalizadas aquí
      resultado = true;
      BancoId=document.getElementById('BancoId').value;
      opcionSeleccionadaBanco = document.getElementById('BancoId').selectedOptions[0].textContent;
      TipoOperacionId=document.getElementById('TipoOperacionId').value;
      opcionSeleccionadaTipoOperacion = document.getElementById('TipoOperacionId').selectedOptions[0].textContent;
      MontoEfectivo=document.getElementById('MontoEfectivo').value;
      Comision=document.getElementById('Comision').value;
      numerooperacion=document.getElementById('numerooperacion').value;
      Comentario=document.getElementById('Comentario').value;

      resultado = true;
      if (BancoId =="") {
        alert ("Seleccionar BANCO.");
        resultado = false;
      }

      if (TipoOperacionId=="") {
        alert ("Seleccionar TIPO DE OPERACIÓN.");
        resultado = false;
      }

      if (MontoEfectivo =="") {
        alert ("Ingresa un MONTO diferente a VACIO. ");
        resultado = false;
      }

      if (numerooperacion =="") {
        alert ("Ingresa un Nro. de Operaciones diferente a VACIO. ");
        resultado = false;
      }

      if (parseInt(numerooperacion)<=0) {
        alert ("Ingresa un Nro. de Operaciones mayor a CERO");
        resultado = false;
      }

      if (Comision =="") {
        alert ("Ingresa un COMISION diferente a VACIO. ");
        resultado = false;
      }

       if (opcionSeleccionadaBanco.includes("YAPE")) {
            if (parseInt(Comision)<=0){
                alert ("La COMISION no puede ser CERO en YAPE");
                resultado=false;
            }
       }
       //En caso no ser una RECARGA DE SALDO  se va mostrar las siguientes alertas informativas
       if (Comentario.includes("SALDO")==false){
        alertasInformativas(opcionSeleccionadaBanco,opcionSeleccionadaTipoOperacion);
       }

      if (resultado){
        // Aquí puedes realizar el envío del formulario o cualquier otra acción necesaria
        //alert("Formulario enviado con éxito.");
        formulario.submit(); // Puedes habilitar esta línea si deseas enviar el formulario automáticamente
        document.getElementById('btnRegistrar').disabled = true;
      }
    });

  }

    //Formulario CompraVenta - Agente
  if($("#formRegistarCompraVentaDolar").length==1){

    enviarMonto ();
    $("#enviar").keypress(function(){
      enviarMonto ();
    });

    $("#enviar").on("keydown", function(event) {
      enviarMonto ();
    });

    $("#enviar").on("keyup", function(event) {
      enviarMonto ();
    });

    $("#recibir").keypress(function(){
      recibirMonto ();
    });

    $("#recibir").on("keydown", function(event) {
      recibirMonto ();
    });

    $("#recibir").on("keyup", function(event) {
      recibirMonto ();
    });

    $("#valor_compra").keypress(function(){
      enviarMonto ();
    });

    $("#valor_compra").on("keydown", function(event) {
      enviarMonto ();
    });

     $("#valor_compra").on("keyup", function(event) {
      enviarMonto ();
    });

    $("#valor_venta").keypress(function(){
      enviarMonto ();
    });

    $("#valor_venta").on("keydown", function(event) {
      enviarMonto ();
    });

    $("#valor_venta").on("keyup", function(event) {
      enviarMonto ();
    });

    $("#CancelaCon").keypress(function(){
      enviarMonto ();
    });

    $("#CancelaCon").on("keydown", function(event) {
      enviarMonto ();
    });

    $("#CancelaCon").on("keyup", function(event) {
      enviarMonto ();
    });

  }

  //Formulario Ingreso Egreso
  if($("#formIngresoEgreso").length==1){
        function completarComnetario () {
            var selectElementoBanco     = document.getElementById("BancoId");
            var BancoId                 = selectElementoBanco.selectedIndex;
            var textoSeleccionadoBanco  = selectElementoBanco.options[BancoId].text;

            var selectElementoMes       = document.getElementById("Mes");
            var Mes                     = selectElementoMes.selectedIndex;
            var textoSeleccionadoMes    = selectElementoMes.options[Mes].text;

            document.getElementById('comentario').value = textoSeleccionadoBanco + " - COMISION:" + textoSeleccionadoMes;
        }
        completarComnetario ();
        $('#BancoId').change(function() {
          completarComnetario ();
        });
        $('#Mes').change(function() {
          completarComnetario ();
        });
  }

  //Atajos para ir a una pagina mediante teclado
  $(document).on('keydown', function(event) {
      if (event.which == 114) { // 114 es el código de la tecla F3
        window.location.href = '/nuevaOperacion'; // redirige a la página de ayuda
        return false; // evita que se propague el evento
      }
      if (event.which == 115) { // 115 es el código de la tecla F4
        window.location.href = '/compraventadolar'; // redirige a la página de ayuda
        return false; // evita que se propague el evento
      }
      if (event.which == 116) { // 116 es el código de la tecla F5
        window.location.href = '/home'; // redirige a la página de ayuda
        return false; // evita que se propague el evento
      }
      if (event.which == 117) { // 117 es el código de la tecla F6
        window.location.href = '/cajaCierre'; // redirige a la página de ayuda
        return false; // evita que se propague el evento
      }
      if (event.which == 118) { // 118 es el código de la tecla F7
        window.location.href = '/nuevaOperacionWu'; // redirige a la página de ayuda
        return false; // evita que se propague el evento
      }
      if (event.which == 119) { // 119 es el código de la tecla F8
        window.location.href = '/compraventadolarWu'; // redirige a la página de ayuda
        return false; // evita que se propague el evento
      }
      if (event.which == 120) { // 120 es el código de la tecla F9
        window.location.href = '/listaOperacionWu'; // redirige a la página de ayuda
        return false; // evita que se propague el evento
      }
      if (event.which == 121) { // 121 es el código de la tecla F10
        window.location.href = '/cierreCajaWu'; // redirige a la página de ayuda
        return false; // evita que se propague el evento
      }
  });

  if($("#formListaRemesa").length==1){
        //Sumar totales de las filas en el footer
            // Obtén la tabla y las celdas del footer
            var tabla = document.getElementById('tableData');
            var celdasFooter = tabla.tFoot.rows[0].cells;
            var simboloMoneda = document.getElementById('TipoMonedaId').selectedOptions[0].innerText
            // Inicializa los totales
            var totalColumna3 = 0,
                totalColumna4 = 0,
                totalColumna5 = 0;

            // Recorre las filas de datos y suma los valores de las últimas 3 columnas
            for (var i = 0; i < tabla.tBodies[0].rows.length; i++) {
              var fila = tabla.tBodies[0].rows[i];
              totalColumna3 += parseFloat(fila.cells[2].innerText) || 0;
              totalColumna4 += parseFloat(fila.cells[3].innerText) || 0;
              totalColumna5 += parseFloat(fila.cells[4].innerText) || 0;
            }

            // Actualiza las celdas del footer con los totales calculados
            celdasFooter[2].innerText = simboloMoneda + " "+ totalColumna3;
            celdasFooter[3].innerText = simboloMoneda + " "+ totalColumna4;
            celdasFooter[4].innerText = simboloMoneda + " "+ totalColumna5;
  }
});

function buscarAperturaCaja (boton) {
    $('#operacion').val("Buscar");
    document.getElementById('apertuCajaAgenteForm').submit();
}

function alertaAperturaCaja (boton) {
    var operacionValue = $('#operacion').val();
    if (operacionValue=="Eliminar"){
            result = confirm('¿Estas seguro de eliminar la caja?. Tener en consideración que se eliminará todas las operaciones del día. En caso se elimine por error, comunicar al DMINISTRADOR')
    }
    else {
            result=true;
    }
    return result;
}

function eliminarAperturaCaja(boton) {
    //var btn= document.getElementsByName('accion_btn')[1].innerHTML;
    //debugger;

    $('#operacion').val("Eliminar");

    //if (true){
    //        result = confirm('¿Estas seguro de eliminar la caja?. Tener en consideración que se eliminará todas las operaciones del día.')
    //}
    //else {
    //        result=true;
    //}

    //if (result){
    //    document.getElementById('apertuCajaAgenteForm').submit();
    //}
}

  //validacion de contraseña inicio
  function validatePassword()
  {
    var password = document.getElementById("password");
    var confirm_password = document.getElementById("confirm_password");
    if(password.value != confirm_password.value) {
      $("#confirm_password").addClass('is-invalid');
      $("#confirm_password").removeClass('is-valid');
    } else {
      $("#confirm_password").addClass('is-valid');
    }
  }

  //validacion de contraseña fin

  //funciones de validacion inicio

  function isNumberKey(evt)
  {
    var charCode = (evt.which) ? evt.which : evt.keyCode;
    if (charCode != 46 && charCode > 31 
    && (charCode < 48 || charCode > 57))
    return false;
    return true;
  }

  function isNumericKey(evt)
  {
    var charCode = (evt.which) ? evt.which : evt.keyCode;
    if (charCode != 46 && charCode > 31 
    && (charCode < 48 || charCode > 57))
    return true;
    return false;
  }
  //funciones de validacion fin

/*
document.getElementById('iframe').scrollTop = -438;

var myIframe = document.getElementById('iframe');
myIframe.onload = function () {
    myIframe.contentWindow.scrollTo(100px,100px);
}*/

//Deshabilitar boton luego de clic en formulario nueva operacion
function clickRegistrarOperacion(boton) {
  //boton.disabled = true;
}



function calcularVuelto(){
      var CancelaCon        =  document.getElementById('CancelaCon').value;
      var MontoEfectivo     =  document.getElementById('MontoEfectivo').value;
      var MontoBanco        =  document.getElementById('MontoBanco').value;
      var MontoTotal        = parseFloat(MontoEfectivo) + parseFloat(MontoBanco);
      document.getElementById('MontoTotal').innerHTML  = MontoTotal;
      var Comision          =  document.getElementById('Comision').value;

      var vuelto            = parseFloat(CancelaCon) - parseFloat(MontoTotal) - parseFloat(Comision);

     /* if (isNaN(vuelto) || isNaN(document.getElementById('vuelto').value)) {
        vuelto = 0;
      }*/

      document.getElementById('vuelto').value       ="S/ "+ vuelto;
      document.getElementById('vuelto').innerHTML   ="S/ "+ vuelto;

      //actualizar href de boton imprimir
      var selectElemento    = document.getElementById("TipoOperacionId");
      var TipoOperacionId   = selectElemento.selectedIndex;
      var textoSeleccionado = selectElemento.options[TipoOperacionId].text;
      var imprimir_btn      = document.getElementById('imprimir_btn');

      imprimir_btn.href = window.location.origin + "/imprimirNuevaOperacion/" + MontoTotal + "/" + Comision + "/" + textoSeleccionado;
}


function alertasInformativas(opcionSeleccionadaBanco,opcionSeleccionadaTipoOperacion){
    if (opcionSeleccionadaBanco.includes("YAPE")) {
      if (opcionSeleccionadaTipoOperacion.includes("RETIRO")) {
            alert ("Solicitar al cliente que haga el YAPE al instante  y desde su celular para evitar FRAUDE.");
      }
    }

    if (opcionSeleccionadaBanco.includes("BCP") || opcionSeleccionadaBanco.includes("BANCA MOVIL INTERBANK") || opcionSeleccionadaBanco.includes("SCOTIABANK/PLIN")) {
      if (opcionSeleccionadaTipoOperacion.includes("RETIRO")) {
        alert ("Validar con ADMINISTRADOR los retiros desde BANCA MOVIL (BCP, INTERBANK, SCOTIABANK).")
      }
    }
}

function clickRegistrarCompraYVentaDolar(boton) {
  boton.disabled = true;
  document.getElementById('formRegistarCompraVentaDolar').submit();
}

function clickRegistrarTransferirWuForm(boton) {
  boton.disabled = true;
  document.getElementById('transferirWuForm').submit();
}


function scrollDiv(){
    var div = document.getElementById('iframe');
    div.scrollTop  = '9999';
}

//Formulario nuevaOperacionWu
function calcularMontoDiferenciaEnSoles() {
  montoDolarWu = document.getElementById('montoDolarWu').value;
  montoDolarCaja = document.getElementById('montoDolarCaja').value;
  valor_compra = document.getElementById('tipoCambioCompra').value;
  valor_venta = document.getElementById('tipoCambioVenta').value;

  tipoOperacionIdDolar = document.getElementById('tipoOperacionIdDolar').value;
  montoDiferenciaDolar = montoDolarWu - montoDolarCaja;

  //Validacion tipoOperacionIdDolar
  if (parseInt(montoDolarCaja)>parseInt(montoDolarWu) && parseInt(tipoOperacionIdDolar)==1){
    alert("El monto dolar a retirar de caja no puede ser mayor al que figura en WU");
    document.getElementById('montoDolarWu').value = 0;
    document.getElementById('montoDolarCaja').value = 0;
    return;
  }

  //1:Salida de Efectivo (RETIRO)
  if (tipoOperacionIdDolar==="1"){
    montoSolCaja = montoDiferenciaDolar * valor_compra
    document.getElementById('tipoCambioCompra').style.fontWeight = 'bold';
    document.getElementById('tipoCambioVenta').style.fontWeight = 'normal';
    $("#tipoCambioCompra").addClass("bg-secondary text-white");
    $("#tipoCambioVenta").removeClass("bg-secondary text-white");
  }
  else {
    if (montoDiferenciaDolar<0){
        montoSolCaja = montoDiferenciaDolar * valor_compra
        document.getElementById('tipoCambioCompra').style.fontWeight = 'bold';
        document.getElementById('tipoCambioVenta').style.fontWeight = 'normal';
        $("#tipoCambioCompra").addClass("bg-secondary text-white");
        $("#tipoCambioVenta").removeClass("bg-secondary text-white");
    }
    else {
        montoSolCaja = montoDiferenciaDolar * valor_venta
        document.getElementById('tipoCambioVenta').style.fontWeight = 'bold';
        document.getElementById('tipoCambioCompra').style.fontWeight = 'normal';
        $("#tipoCambioVenta").addClass("bg-secondary text-white");
        $("#tipoCambioCompra").removeClass("bg-secondary text-white");
    }
  }
  document.getElementById('montoSolCaja').value = montoSolCaja.toFixed(3);
}

function launchFullScreen(element) {
  if(element.requestFullScreen) {
    element.requestFullScreen();
  } else if(element.mozRequestFullScreen) {
    element.mozRequestFullScreen();
  } else if(element.webkitRequestFullScreen) {
    element.webkitRequestFullScreen();
  }
}
// Lanza en pantalla completa en navegadores que lo soporten
 function cancelFullScreen() {
     if(document.cancelFullScreen) {
         document.cancelFullScreen();
     } else if(document.mozCancelFullScreen) {
         document.mozCancelFullScreen();
     } else if(document.webkitCancelFullScreen) {
         document.webkitCancelFullScreen();
     }
 }

//Formulario cierreFormWu

 function copyValue(rowId, cajaId) {

        // Obtén el valor de la segunda columna
        var montoInicial = document.getElementById('montoinicial_' + rowId).value;

        // Crea un elemento de texto temporal
        var tempInput = document.createElement('input');
        tempInput.value = montoInicial;

        // Agrega el elemento temporal al cuerpo del documento
        document.body.appendChild(tempInput);

        // Selecciona y copia el contenido del elemento temporal
        tempInput.select();
        document.execCommand('copy');

        // Elimina el elemento temporal
        document.body.removeChild(tempInput);

        // Puedes agregar una alerta o cualquier otra acción después de la copia
        document.getElementById(cajaId).value = montoInicial;
 }

 // Generar carrusel

     // Cargar JSON y generar carrusel
 fetch('/get_textos')
      .then(response => response.json())
      .then(data => generarCarrusel(JSON.parse(data)));

function generarCarrusel(textos) {

      var indicadores = document.getElementById('indicadores');
      var contenidoCarrusel = document.getElementById('contenidoCarrusel');

      textos.forEach(function(texto, index) {
        // Agregar indicadores
       /* var indicador = document.createElement('li');
        indicador.setAttribute('data-bs-target', '#miCarrusel');
        indicador.setAttribute('data-bs-slide-to', index.toString());
        if (index === 0) {
          indicador.classList.add('active');
        }
        indicadores.appendChild(indicador);*/

        // Agregar contenido del carrusel
        var slide = document.createElement('div');
        slide.classList.add('carousel-item');
        if (index === 0) {
          slide.classList.add('active');
        }

        var contenido = document.createElement('div');
        contenido.classList.add('d-block', 'w-100', 'text-center');

        var titulo = document.createElement('h5');
        titulo.innerText = texto.titulo;

        var descripcion = document.createElement('p');
        descripcion.innerText = texto.descripcion;

        /*contenido.appendChild(titulo);*/
        contenido.appendChild(descripcion);
        slide.appendChild(contenido);
        contenidoCarrusel.appendChild(slide);
      });
}