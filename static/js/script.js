// Carrega os produtos do backend na tabela de montagem da cesta
async function carregarProdutosParaCesta() {
  try {
    const res = await axios.get("/produtos");
    const tbody = document.querySelector("#tabela-produtos tbody");
    tbody.innerHTML = "";

    res.data.forEach((p) => {
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td>${p.descricao}</td>
        <td>${p.marca}</td>
        <td>${p.quantidade}</td>
        <td>R$ ${p.valor.toFixed(2)}</td>
        <td>
          <input type="number" class="form-control form-control-sm"
            min="0" max="${p.quantidade}" value="0"
            data-descricao="${p.descricao}"
            data-marca="${p.marca}"
            data-valor="${p.valor}"
            style="width: 80px;">
        </td>
      `;

      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Erro ao carregar produtos para cesta:", err);
  }
}

// Função para gerar e enviar a cesta e abrir PDF
async function gerarCesta() {
  const inputs = document.querySelectorAll("#tabela-produtos input[type='number']");
  const itens = [];

  inputs.forEach(input => {
    const qtd = parseInt(input.value);
    if (!qtd || qtd <= 0) return;

    itens.push({
      descricao: input.dataset.descricao,
      marca: input.dataset.marca,
      quantidade: qtd
    });
  });

  if (itens.length === 0) {
    alert("Selecione pelo menos um item com quantidade.");
    return;
  }

  try {
    const res = await axios.post("/api/montar_cesta", { itens }, { responseType: 'blob' });

    const blob = new Blob([res.data], { type: 'application/pdf' });
    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.target = "_blank";
    link.click();
  } catch (err) {
    console.error("Erro ao gerar cesta:", err);
    alert("Erro ao gerar a cesta.");
  }
}

// Inicializa ao carregar a página
document.addEventListener("DOMContentLoaded", () => {
  carregarProdutosParaCesta();
});
