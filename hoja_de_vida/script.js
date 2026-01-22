function downloadPDF(){
    
    const element =document.querySelector('#pdf-content');

    //console.log("element");
    const otp ={
        margin: [10, 5, 15, 5], //[arriba,izquierda,abajo,derecha] en mm
        filename: 'hoja_de_vida_jorge_arias.pdf',
        image:{ type:'jpeg', quality: 1 },
        html2canvas:{
            scale: 2,
            useCORS: true,
            scrollY:0
        },
        jsPDF:{
            format:'a4',
            orientation:'portrait'//orientacion vertical

        }

    }
    html2pdf().set(otp).from(element).save();
}