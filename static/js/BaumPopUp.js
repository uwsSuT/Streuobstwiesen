
function BaumPopUp(feature, layer) {
    var text = "<table> <tr> <th> Baum Nr. </th>" +
                         "<td>" + layer.feature.properties.baum_nr + "</td>" +
                    "</tr>" +
                    "<tr>" +
        '<td colspan="2">' + 
            '<a href="/wiese/baum/' + String(layer.feature.properties.baum_nr) + '">'  + 
        (layer.feature.properties.baum_pic !== null ? '<img src="' + String(layer.feature.properties.baum_pic) + '" style="width:200px">' : '') + '</a>' + '</td>' +
                    "</tr>" +
                    "<tr> <th> Art </th>" +
                         "<td>" + layer.feature.properties.obst_type + "</td>" +
                    "</tr>" +
                    "<tr> <th> Sorte </th>" +
                         "<td>" + layer.feature.properties.sorte + "</td>" +
                    "</tr> </table>";
    layer.bindPopup(text);
    // ACHTUGNG: Dem ToolTip muss ein TEXT übergeben werden; Daher das '"" +'
    // Ist wohl eher nicht gewünscht
    // layer.bindTooltip("" + layer.feature.properties.baum_nr, {permanent: true});
}
