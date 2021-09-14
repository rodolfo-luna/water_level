<?php
$distancia = filter_input(INPUT_GET, 'distancia', FILTER_SANITIZE_NUMBER_FLOAT);
$hora = filter_input(INPUT_GET,'hora', FILTER_SANITIZE_SPECIAL_CHARS);
if (!empty($distancia) || !empty($hora)) {
    $dados = array($distancia, $hora);
    $arquivo = fopen('/home/pi/Documents/webservice_caixa_dagua/ultrasonico.csv', 'a+');
    fputcsv($arquivo, array_values($dados));
    fclose($arquivo); 
    print_r(array_values($dados));
} else {
    die("Dados inválidos");
}
?>