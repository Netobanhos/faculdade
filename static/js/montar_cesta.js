document.addEventListener("DOMContentLoaded", async () => {
  const tabela = document.getElementById("tabelaCestaProdutos");

  try {
    const res = await axios.get("/produtos");

    res.data.forEach(p => {
      const linha = document.createElement("tr");
      linha.innerHTML = `
        <td data-label="Descrição">${p.descricao}</td>
        <td data-label="Marca">${p.marca}</td>
        <td data-label="Estoque">${p.quantidade}</td>
        <td data-label="Valor Unitário">R$ ${p.valor.toFixed(2)}</td>
        <td data-label="Qtd na Cesta">
          <input type="number" min="0" max="${p.quantidade}" data-descricao="${p.descricao}" data-marca="${p.marca}" data-valor="${p.valor}" />
        </td>
      `;
      tabela.appendChild(linha);
    });
  } catch (err) {
    console.error("Erro ao carregar produtos:", err);
  }
});

async function gerarCesta() {
  const inputs = document.querySelectorAll("input[type='number']");
  const itens = [];

  inputs.forEach(input => {
    const qtd = parseInt(input.value);
    if (qtd && qtd > 0) {
      itens.push({
        descricao: input.dataset.descricao,
        marca: input.dataset.marca,
        quantidade: qtd
      });
    }
  });

  if (itens.length === 0) {
    alert("Selecione pelo menos um item com quantidade.");
    return;
  }

  try {
    const res = await axios.post("/api/montar_cesta", { itens }, { responseType: 'blob' });

    const blob = new Blob([res.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    window.open(url, '_blank');
  } catch (err) {
    alert("Erro ao gerar o PDF.");
    console.error(err);
  }
}
