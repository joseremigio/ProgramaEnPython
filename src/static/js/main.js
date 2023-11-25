(function ($) {
     /*document.getElementById('startDate').value = new Date().toISOString().slice(0, 10);
     document.getElementById('endDate').value = new Date().toISOString().slice(0, 10);*/

    //Seleccionar por defecto deposito cuando es wester
    $("#BancoId").change(function (){
        //Wester - Pago de Servicio, se seleccione DEPOSTIO
        if ($(this).val()[0] =="4"){
            //debugger;
            $("#TipoOperacionId")[0][2].defaultSelected=true;
            //$("#TipoOperacionId")[0][2].Selected=true;
        }
        else {
            $("#TipoOperacionId").val(0)
        }
        //Wester - Remesa , se habilita $
        if ($(this).val()[0] =="15"){
            $("#TipoMonedaSol").prop( "disabled", false );
            $("#TipoMonedaDolar").prop( "disabled", true );
            $("#TipoMonedaSol").prop( "checked", true );
            $("#Comision").prop( "readonly", true );

        }
        else if ($(this).val()[0] =="17"){
            $("#TipoMonedaDolar").prop( "disabled", false );
            $("#TipoMonedaSol").prop( "disabled", true );
            $("#TipoMonedaDolar").prop( "checked", true );
            $("#Comision").prop( "readonly", true );
        }
        else {
            $("#TipoMonedaSol").prop( "disabled", false );
            $("#TipoMonedaDolar").prop( "disabled", true );
            $("#TipoMonedaSol").prop( "checked", true );
            $("#Comision").prop( "readonly", false );
        }
    });

    /*$("#TipoMonedaSolVuelto").click(function (){
        $("#TipoMonedaDolarVuelto").prop( "checked", false );
    });

    $("#TipoMonedaDolarVuelto").click(function (){
        $("#TipoMonedaSolVuelto").prop( "checked", false );
    });*/

    /*$("#CompraDolar").click(function (){
       $("#EtiquetaMontoInicio").text("Depositan Dolares");
       $("#EtiquetaMontoFinal").text("Entregas Soles");
       $("#TipoCambioVenta").prop( "disabled", true );
       $("#TipoCambioCompra").prop( "disabled", false );
    });*/

  /* $("#VentaDolar").click(function (){
        $("#EtiquetaMontoInicio").text("Depositan Soles");
        $("#EtiquetaMontoFinal").text("Entregas Dolares");
        $("#TipoCambioCompra").prop( "disabled", true );
        $("#TipoCambioVenta").prop( "disabled", false );
    });*/

    /*$("#MontoInicio").change(function (){
        MontoFinal= 0;
        if ($("#VentaDolar").prop("checked")){
            MontoFinal = $("#MontoInicio").val() *  $("#TipoCambioCompra").val();
        }
        $("#MontoFinal").val(MontoFinal);
    });*/

    $( "select" )
      .change(function () {
        var str = "";
        var contador=0
        $( "select option:selected" ).each(function() {
           contador=contador+1
           if (contador<=2) {
                str += $( this ).text() + ", ";
           }
        });
         $("#bancoNombreYtipoOperacionNombre").val(str);
      })
      .change();

    //Cargar mes y año del modulo de reporte
    var f = new Date();
    var mes=f.getMonth() +1;
    var anio=f.getFullYear();

    if (localStorage.getItem('anio')=== null || localStorage.getItem('anio')==='undefined') {
        $( "#anio" ).val(anio);
    }
    else {
        $( "#anio" ).val(localStorage.getItem('anio'));
        anio = localStorage.getItem('anio')
    }
    if (localStorage.getItem('mes')=== null) {
        $( "#mes" ).val(mes);
    }
    else {
        $( "#mes" ).val(localStorage.getItem('mes'));
        mes = localStorage.getItem('mes')
    }

    $("#buscaeReporteMenu").attr("href", "/reporte/" + anio + "/"+  mes)
    $("#buscaeReporte").attr("href", "/reporte/" + $( "#anio" ).val() + "/"+  $( "#mes" ).val())

    $( "#anio" ).change(function() {
        $("#buscaeReporte").attr("href", "/reporte/" + $( "#anio" ).val() + "/"+  $( "#mes" ).val())
        $("#buscaeReporteMenu").attr("href", "/reporte/" + $( "#anio" ).val() + "/"+  $( "#mes" ).val())
        localStorage.setItem('anio', $( "#anio" ).val());
        localStorage.setItem('mes', $( "#mes" ).val());
    });

    $( "#mes" ).change(function() {
        $("#buscaeReporte").attr("href", "/reporte/" + $( "#anio" ).val() + "/"+  $( "#mes" ).val())
        $("#buscaeReporteMenu").attr("href", "/reporte/" + $( "#anio" ).val() + "/"+  $( "#mes" ).val())
        localStorage.setItem('anio', $( "#anio" ).val());
        localStorage.setItem('mes', $( "#mes" ).val());
    });



    $("#buscarAsistenciaMenu").attr("href", "/asistencia/" + anio + "/"+  mes)
    $("#buscarAsistencia").attr("href", "/asistencia/" + $( "#anio" ).val() + "/"+  $( "#mes" ).val())

    $( "#anio" ).change(function() {
        $("#buscarAsistencia").attr("href", "/asistencia/" + $( "#anio" ).val() + "/"+  $( "#mes" ).val())
        $("#buscarAsistenciaMenu").attr("href", "/asistencia/" + $( "#anio" ).val() + "/"+  $( "#mes" ).val())
        localStorage.setItem('anio', $( "#anio" ).val());
        localStorage.setItem('mes', $( "#mes" ).val());
    });

    $( "#mes" ).change(function() {
        $("#buscarAsistencia").attr("href", "/asistencia/" + $( "#anio" ).val() + "/"+  $( "#mes" ).val())
        $("#buscarAsistenciaMenu").attr("href", "/asistencia/" + $( "#anio" ).val() + "/"+  $( "#mes" ).val())
        localStorage.setItem('anio', $( "#anio" ).val());
        localStorage.setItem('mes', $( "#mes" ).val());
    });

    // Fin Cargar mes y año


    /*"use strict";*/

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();
    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Sidebar Toggler
    $('.sidebar-toggler').click(function () {
        $('.sidebar, .content').toggleClass("open");
        return false;
    });


    // Progress Bar
    $('.pg-bar').waypoint(function () {
        $('.progress .progress-bar').each(function () {
            $(this).css("width", $(this).attr("aria-valuenow") + '%');
        });
    }, {offset: '80%'});


    // Calender
    $('#calender').datetimepicker({
        inline: true,
        format: 'L'
    });


    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        items: 1,
        dots: true,
        loop: true,
        nav : false
    });

    // Salse & Revenue Chart
    var ctx2 = $("#salse-revenue").get(0).getContext("2d");
    var myChart2 = new Chart(ctx2, {
        type: "line",
        data: {
            labels: dias,
            datasets: [{
                    label: "Monto Inicial",
                    data: montosiniciales,
                    backgroundColor: "rgba(0, 156, 255, .5)",
                    fill: true
                },
                {
                    label: "Monto Final Calculado",
                    data: montosfinalcalculados,
                    backgroundColor: "rgba(0, 156, 255, .3)",
                    fill: true
                },
                {
                    label: "Monto Final Real",
                    data: montosfinalreales,
                    backgroundColor: "rgba(54, 255, 51 , .3)",
                    fill: true
                }


            ]
            },
        options: {
            responsive: true
        }
    });


    // Worldwide Sales Chart
    /*var ctx1 = $("#worldwide-sales").get(0).getContext("2d");
    var myChart1 = new Chart(ctx1, {
        type: "bar",
        data: {
            labels: ["2016", "2017", "2018", "2019", "2020", "2021", "2022"],
            datasets: [{
                    label: "USA",
                    data: [15, 30, 55, 65, 60, 80, 95],
                    backgroundColor: "rgba(0, 156, 255, .7)"
                },
                {
                    label: "UK",
                    data: [8, 35, 40, 60, 70, 55, 75],
                    backgroundColor: "rgba(0, 156, 255, .5)"
                },
                {
                    label: "AU",
                    data: [12, 25, 45, 55, 65, 70, 60],
                    backgroundColor: "rgba(0, 156, 255, .3)"
                }
            ]
            },
        options: {
            responsive: true
        }
    });





    // Single Line Chart
    var ctx3 = $("#line-chart").get(0).getContext("2d");
    var myChart3 = new Chart(ctx3, {
        type: "line",
        data: {
            labels: [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150],
            datasets: [{
                label: "Salse",
                fill: false,
                backgroundColor: "rgba(0, 156, 255, .3)",
                data: [7, 8, 8, 9, 9, 9, 10, 11, 14, 14, 15]
            }]
        },
        options: {
            responsive: true
        }
    });


    // Single Bar Chart
    var ctx4 = $("#bar-chart").get(0).getContext("2d");
    var myChart4 = new Chart(ctx4, {
        type: "bar",
        data: {
            labels: ["Italy", "France", "Spain", "USA", "Argentina"],
            datasets: [{
                backgroundColor: [
                    "rgba(0, 156, 255, .7)",
                    "rgba(0, 156, 255, .6)",
                    "rgba(0, 156, 255, .5)",
                    "rgba(0, 156, 255, .4)",
                    "rgba(0, 156, 255, .3)"
                ],
                data: [55, 49, 44, 24, 15]
            }]
        },
        options: {
            responsive: true
        }
    });


    // Pie Chart
    var ctx5 = $("#pie-chart").get(0).getContext("2d");
    var myChart5 = new Chart(ctx5, {
        type: "pie",
        data: {
            labels: ["Italy", "France", "Spain", "USA", "Argentina"],
            datasets: [{
                backgroundColor: [
                    "rgba(0, 156, 255, .7)",
                    "rgba(0, 156, 255, .6)",
                    "rgba(0, 156, 255, .5)",
                    "rgba(0, 156, 255, .4)",
                    "rgba(0, 156, 255, .3)"
                ],
                data: [55, 49, 44, 24, 15]
            }]
        },
        options: {
            responsive: true
        }
    });


    // Doughnut Chart
    var ctx6 = $("#doughnut-chart").get(0).getContext("2d");
    var myChart6 = new Chart(ctx6, {
        type: "doughnut",
        data: {
            labels: ["Italy", "France", "Spain", "USA", "Argentina"],
            datasets: [{
                backgroundColor: [
                    "rgba(0, 156, 255, .7)",
                    "rgba(0, 156, 255, .6)",
                    "rgba(0, 156, 255, .5)",
                    "rgba(0, 156, 255, .4)",
                    "rgba(0, 156, 255, .3)"
                ],
                data: [55, 49, 44, 24, 15]
            }]
        },
        options: {
            responsive: true
        }
    });*/


})(jQuery);




