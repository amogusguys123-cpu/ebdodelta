--[[
    TREINAMENTO FÍSICO - PRAÇAS E GRADUADOS
    LocalScript para uso em uma experiência autorizada no Roblox.

    O painel é um auxiliar de avaliação manual:
    - não lê dados escondidos de outros jogadores;
    - não automatiza comandos administrativos;
    - não dá pontos sozinho por "quase conseguir";
    - o instrutor confirma os JJs, o texto e a resposta.

    Coloque este arquivo como LocalScript em StarterPlayerScripts
    ou StarterGui. Para salvar resultados no servidor, use um Script
    no servidor com RemoteEvent e valide tudo novamente no servidor.
]]

local Players = game:GetService("Players")
local player = Players.LocalPlayer

local ROLE_ORDER = {"Praças", "Graduados"}
local VERSION_ORDER = {"A", "B", "C", "D"}
local DEVICE_ORDER = {"PC/Console", "Celular"}

local RULES = {
    ["Praças"] = {
        jj = 150,
        jjTime = 210,
        pass = 4,
        parkours = {
            A = {35, 40, 30, 32},
            B = {30, 35, 30, 28},
            C = {30, 35, 35, 40},
            D = {35, 30, 30, 40},
        },
    },
    ["Graduados"] = {
        jj = 170,
        jjTime = 230,
        pass = 5,
        parkours = {
            A = {30, 35, 27, 29},
            B = {27, 30, 27, 25},
            C = {25, 27, 27, 30},
            D = {27, 25, 25, 30},
        },
    },
}

local role = "Praças"
local version = "A"
local device = "PC/Console"
local participants = {}
local nextId = 0
local rowFrames = {}

local COLORS = {
    bg = Color3.fromRGB(20, 25, 32),
    panel = Color3.fromRGB(31, 39, 49),
    panel2 = Color3.fromRGB(39, 49, 62),
    accent = Color3.fromRGB(42, 143, 92),
    accent2 = Color3.fromRGB(61, 173, 111),
    text = Color3.fromRGB(239, 244, 246),
    muted = Color3.fromRGB(170, 181, 191),
    red = Color3.fromRGB(184, 70, 70),
    orange = Color3.fromRGB(203, 139, 57),
}

local gui = Instance.new("ScreenGui")
gui.Name = "TreinamentoFisicoGUI"
gui.ResetOnSpawn = false
gui.DisplayOrder = 50
gui.Parent = player:WaitForChild("PlayerGui")

local main = Instance.new("Frame")
main.Name = "Painel"
main.Size = UDim2.fromOffset(980, 650)
main.Position = UDim2.new(0.5, -490, 0.5, -325)
main.BackgroundColor3 = COLORS.bg
main.BorderSizePixel = 0
main.Parent = gui

local mainCorner = Instance.new("UICorner")
mainCorner.CornerRadius = UDim.new(0, 10)
mainCorner.Parent = main

local function label(parent, text, size, position, color, textSize)
    local object = Instance.new("TextLabel")
    object.BackgroundTransparency = 1
    object.Text = text
    object.TextColor3 = color or COLORS.text
    object.TextSize = textSize or 14
    object.Font = Enum.Font.Gotham
    object.TextXAlignment = Enum.TextXAlignment.Left
    object.TextYAlignment = Enum.TextYAlignment.Center
    object.Size = size
    object.Position = position
    object.Parent = parent
    return object
end

local function button(parent, text, size, position, callback, color)
    local object = Instance.new("TextButton")
    object.AutoButtonColor = true
    object.BackgroundColor3 = color or COLORS.panel2
    object.BorderSizePixel = 0
    object.Text = text
    object.TextColor3 = COLORS.text
    object.TextSize = 12
    object.Font = Enum.Font.GothamSemibold
    object.Size = size
    object.Position = position
    object.Parent = parent
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 5)
    corner.Parent = object
    object.MouseButton1Click:Connect(callback)
    return object
end

local function textBox(parent, placeholder, size, position)
    local object = Instance.new("TextBox")
    object.BackgroundColor3 = COLORS.panel2
    object.BorderSizePixel = 0
    object.PlaceholderText = placeholder
    object.PlaceholderColor3 = COLORS.muted
    object.Text = ""
    object.TextColor3 = COLORS.text
    object.TextSize = 12
    object.Font = Enum.Font.Gotham
    object.ClearTextOnFocus = false
    object.Size = size
    object.Position = position
    object.Parent = parent
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 5)
    corner.Parent = object
    return object
end

local titleBar = Instance.new("Frame")
titleBar.BackgroundColor3 = COLORS.accent
titleBar.BorderSizePixel = 0
titleBar.Size = UDim2.new(1, 0, 0, 44)
titleBar.Parent = main

local title = label(titleBar, "TREINAMENTO FÍSICO  •  PAINEL DO INSTRUTOR", UDim2.new(1, -100, 1, 0), UDim2.fromOffset(16, 0), COLORS.text, 16)
title.Font = Enum.Font.GothamBold

local closeButton = button(titleBar, "X", UDim2.fromOffset(34, 28), UDim2.new(1, -44, 0, 8), function()
    gui.Enabled = false
end, COLORS.red)

local minimizeButton = button(titleBar, "—", UDim2.fromOffset(34, 28), UDim2.new(1, -84, 0, 8), function()
    main.Size = main.Size == UDim2.fromOffset(980, 650) and UDim2.fromOffset(980, 44) or UDim2.fromOffset(980, 650)
end, COLORS.panel2)

-- Arrastar a janela pelo título.
local dragging = false
local dragStart
local startPosition
titleBar.InputBegan:Connect(function(input)
    if input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch then
        dragging = true
        dragStart = input.Position
        startPosition = main.Position
        input.Changed:Connect(function()
            if input.UserInputState == Enum.UserInputState.End then
                dragging = false
            end
        end)
    end
end)
titleBar.InputChanged:Connect(function(input)
    if input.UserInputType == Enum.UserInputType.MouseMovement or input.UserInputType == Enum.UserInputType.Touch then
        input.Changed:Connect(function()
            if dragging then
                local delta = input.Position - dragStart
                main.Position = UDim2.new(startPosition.X.Scale, startPosition.X.Offset + delta.X, startPosition.Y.Scale, startPosition.Y.Offset + delta.Y)
            end
        end)
    end
end)

local controls = Instance.new("Frame")
controls.BackgroundColor3 = COLORS.panel
controls.BorderSizePixel = 0
controls.Size = UDim2.new(1, -24, 0, 126)
controls.Position = UDim2.fromOffset(12, 54)
controls.Parent = main

label(controls, "CONFIGURAÇÃO DO TREINAMENTO", UDim2.fromOffset(250, 24), UDim2.fromOffset(12, 7), COLORS.muted, 12)

local roleButton
local versionButton
local deviceButton
local metaLabel
local rankPanel

local function currentRules()
    return RULES[role]
end

local function refreshMeta()
    local rules = currentRules()
    roleButton.Text = "Perfil: " .. role
    versionButton.Text = "Versão: " .. version
    deviceButton.Text = "Torre: " .. device
    metaLabel.Text = string.format(
        "JJ: %d em %ds   |   Texto: 400s   |   Pergunta: 40s   |   Aprovação: %d/%d pontos   |   Torre: %ds",
        rules.jj,
        rules.jjTime,
        rules.pass,
        9,
        device == "Celular" and 16 or 15
    )
end

roleButton = button(controls, "", UDim2.fromOffset(170, 30), UDim2.fromOffset(12, 34), function()
    local index = table.find(ROLE_ORDER, role) or 1
    role = ROLE_ORDER[index % #ROLE_ORDER + 1]
    refreshMeta()
end, COLORS.accent)

versionButton = button(controls, "", UDim2.fromOffset(130, 30), UDim2.fromOffset(192, 34), function()
    local index = table.find(VERSION_ORDER, version) or 1
    version = VERSION_ORDER[index % #VERSION_ORDER + 1]
    refreshMeta()
end)

deviceButton = button(controls, "", UDim2.fromOffset(160, 30), UDim2.fromOffset(334, 34), function()
    local index = table.find(DEVICE_ORDER, device) or 1
    device = DEVICE_ORDER[index % #DEVICE_ORDER + 1]
    refreshMeta()
end)

local patenteButton = button(controls, "Aba: Patente", UDim2.fromOffset(125, 30), UDim2.fromOffset(505, 34), function()
    if rankPanel then
        rankPanel.Visible = not rankPanel.Visible
    end
end, COLORS.orange)

metaLabel = label(controls, "", UDim2.new(1, -24, 0, 24), UDim2.fromOffset(12, 78), COLORS.text, 12)

local infoPanel = Instance.new("Frame")
infoPanel.BackgroundColor3 = COLORS.panel
infoPanel.BorderSizePixel = 0
infoPanel.Size = UDim2.new(1, -24, 0, 58)
infoPanel.Position = UDim2.fromOffset(12, 190)
infoPanel.Parent = main

local instructorBox = textBox(infoPanel, "Instrutor (ex.: @Nick)", UDim2.fromOffset(175, 30), UDim2.fromOffset(10, 14))
local auxiliariesBox = textBox(infoPanel, "Auxiliares (somente oficiais)", UDim2.fromOffset(205, 30), UDim2.fromOffset(195, 14))
local timeBox = textBox(infoPanel, "Horário", UDim2.fromOffset(110, 30), UDim2.fromOffset(415, 14))
local serverBox = textBox(infoPanel, "Código do servidor", UDim2.fromOffset(170, 30), UDim2.fromOffset(535, 14))
local amountBox = textBox(infoPanel, "01/50", UDim2.fromOffset(75, 30), UDim2.fromOffset(715, 14))

local addPanel = Instance.new("Frame")
addPanel.BackgroundColor3 = COLORS.panel
addPanel.BorderSizePixel = 0
addPanel.Size = UDim2.new(1, -24, 0, 42)
addPanel.Position = UDim2.fromOffset(12, 258)
addPanel.Parent = main

local participantBox = textBox(addPanel, "Nome do participante", UDim2.fromOffset(250, 30), UDim2.fromOffset(10, 6))
local statusLabel = label(addPanel, "0 participantes", UDim2.fromOffset(160, 30), UDim2.fromOffset(275, 6), COLORS.muted, 12)

local list = Instance.new("ScrollingFrame")
list.Name = "Participantes"
list.BackgroundColor3 = COLORS.panel
list.BorderSizePixel = 0
list.Position = UDim2.fromOffset(12, 308)
list.Size = UDim2.new(1, -24, 0, 224)
list.ScrollBarThickness = 7
list.CanvasSize = UDim2.fromOffset(0, 0)
list.Parent = main

local listLayout = Instance.new("UIListLayout")
listLayout.Padding = UDim.new(0, 6)
listLayout.SortOrder = Enum.SortOrder.LayoutOrder
listLayout.Parent = list

listLayout:GetPropertyChangedSignal("AbsoluteContentSize"):Connect(function()
    list.CanvasSize = UDim2.fromOffset(0, listLayout.AbsoluteContentSize.Y + 8)
end)

local output = Instance.new("TextBox")
output.Name = "Saida"
output.BackgroundColor3 = Color3.fromRGB(15, 19, 24)
output.BorderSizePixel = 0
output.Position = UDim2.fromOffset(12, 542)
output.Size = UDim2.new(1, -24, 0, 74)
output.TextColor3 = COLORS.text
output.TextSize = 12
output.Font = Enum.Font.Code
output.TextXAlignment = Enum.TextXAlignment.Left
output.TextYAlignment = Enum.TextYAlignment.Top
output.TextWrapped = false
output.ClearTextOnFocus = false
output.MultiLine = true
output.Text = "A saída do anúncio ou relatório aparecerá aqui."
output.Parent = main

local function rounded(parent, radius)
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, radius or 5)
    corner.Parent = parent
end

rounded(controls)
rounded(infoPanel)
rounded(addPanel)
rounded(list)
rounded(output)

-- Aba manual para preparar o comando ;titler.
-- O texto fica selecionável para cópia manual. O toque em um jogador
-- não dispara comandos administrativos.
rankPanel = Instance.new("Frame")
rankPanel.Name = "AbaPatente"
rankPanel.BackgroundColor3 = COLORS.panel
rankPanel.BorderSizePixel = 0
rankPanel.Size = UDim2.fromOffset(500, 190)
rankPanel.Position = UDim2.new(0.5, -250, 0.5, -95)
rankPanel.ZIndex = 20
rankPanel.Visible = false
rankPanel.Parent = main
rounded(rankPanel, 8)

local rankTitle = label(rankPanel, "ENTREGA DE PONTOS / PATENTE", UDim2.new(1, -60, 0, 30), UDim2.fromOffset(16, 10), COLORS.text, 15)
rankTitle.Font = Enum.Font.GothamBold
rankTitle.ZIndex = 21

local rankClose = button(rankPanel, "X", UDim2.fromOffset(30, 26), UDim2.new(1, -42, 0, 10), function()
    rankPanel.Visible = false
end, COLORS.red)
rankClose.ZIndex = 21

local rankNickBox = textBox(rankPanel, "Nick exato do jogador", UDim2.fromOffset(250, 32), UDim2.fromOffset(16, 54))
rankNickBox.ZIndex = 21
local rankPointsBox = textBox(rankPanel, "Quantidade", UDim2.fromOffset(120, 32), UDim2.fromOffset(278, 54))
rankPointsBox.ZIndex = 21

local rankPreview = textBox(rankPanel, "O comando preparado aparecerá aqui.", UDim2.fromOffset(382, 32), UDim2.fromOffset(16, 98))
rankPreview.TextEditable = true
rankPreview.ZIndex = 21

local function prepareTitler()
    local nick = rankNickBox.Text:gsub("^%s+", ""):gsub("%s+$", "")
    local points = rankPointsBox.Text:gsub("%D", "")
    if nick == "" or points == "" then
        rankPreview.Text = "Informe o Nick e uma quantidade numérica."
        return
    end
    rankPreview.Text = ";titler " .. nick .. " " .. points
    output.Text = "Comando preparado para revisão:\n" .. rankPreview.Text .. "\nSelecione o texto e copie manualmente."
end

local prepareButton = button(rankPanel, "Preparar comando", UDim2.fromOffset(120, 32), UDim2.fromOffset(398, 54), prepareTitler, COLORS.accent)
prepareButton.ZIndex = 21

local selectButton = button(rankPanel, "Selecionar texto", UDim2.fromOffset(120, 32), UDim2.fromOffset(398, 98), function()
    if rankPreview.Text ~= "" and rankPreview.Text ~= "O comando preparado aparecerá aqui." then
        rankPreview:CaptureFocus()
        rankPreview.SelectionStart = 1
        rankPreview.CursorPosition = #rankPreview.Text + 1
    end
end)
selectButton.ZIndex = 21

local rankNote = label(rankPanel, "Depois use Ctrl+C no PC ou toque e segure no celular para copiar.", UDim2.fromOffset(460, 28), UDim2.fromOffset(16, 145), COLORS.muted, 10)
rankNote.ZIndex = 21

local function makeParticipant(name)
    nextId += 1
    return {
        id = nextId,
        name = name,
        score = 0,
        awards = {JJ = 0, P1 = 0, P2 = 0, P3 = 0, P4 = 0, TEXT = 0, QUESTION = 0},
        timers = {},
        jjCount = "",
        textErrors = "",
        textTheme = true,
    }
end

local function applyAward(participant, key, value)
    value = math.max(0, value)
    participant.score -= participant.awards[key] or 0
    participant.awards[key] = value
    participant.score += value
end

local function findParticipant(id)
    for _, participant in ipairs(participants) do
        if participant.id == id then
            return participant
        end
    end
end

local function formatSeconds(seconds)
    if not seconds then
        return "--"
    end
    return tostring(seconds) .. "s"
end

local refreshRows

local function toggleTimer(participant, key, limit)
    if not participant.timers[key] then
        participant.timers[key] = {started = os.clock()}
    else
        local timer = participant.timers[key]
        if not timer.elapsed then
            timer.elapsed = math.floor(os.clock() - timer.started + 0.5)
            local passed = timer.elapsed <= limit
            if key == "JJ" then
                local count = tonumber(participant.jjCount) or 0
                passed = passed and count >= currentRules().jj
                applyAward(participant, "JJ", passed and 1 or 0)
            else
                applyAward(participant, key, passed and 1 or 0)
            end
        end
    end
    refreshRows()
end

local function setTextPoints(participant, points)
    local errors = tonumber(participant.textErrors)
    if points == nil then
        if errors == nil or errors < 0 then
            points = 0
        elseif errors == 0 and participant.textTheme then
            points = 2
        elseif errors <= 3 and participant.textTheme then
            points = 1
        else
            points = 0
        end
    end
    applyAward(participant, "TEXT", points)
    refreshRows()
end

local function setQuestionPoints(participant, value)
    applyAward(participant, "QUESTION", value and 1 or 0)
    refreshRows()
end

local function clearRows()
    for _, frame in pairs(rowFrames) do
        frame:Destroy()
    end
    rowFrames = {}
end

local function addSmallButton(parent, text, x, width, callback, color)
    return button(parent, text, UDim2.fromOffset(width, 26), UDim2.fromOffset(x, 40), callback, color)
end

refreshRows = function()
    clearRows()
    statusLabel.Text = tostring(#participants) .. " participante(s)"
    local rules = currentRules()
    local parkourLimits = rules.parkours[version]

    for index, participant in ipairs(participants) do
        local row = Instance.new("Frame")
        row.Name = "Participante_" .. participant.id
        row.BackgroundColor3 = COLORS.panel2
        row.BorderSizePixel = 0
        row.Size = UDim2.new(1, -12, 0, 96)
        row.LayoutOrder = index
        row.Parent = list
        rounded(row, 6)
        rowFrames[participant.id] = row

        local result = participant.score >= rules.pass and "APROVADO" or "EM AVALIAÇÃO"
        local resultColor = participant.score >= rules.pass and COLORS.accent2 or COLORS.muted
        local nameLabel = label(row, participant.name, UDim2.fromOffset(180, 26), UDim2.fromOffset(10, 7), COLORS.text, 14)
        nameLabel.Font = Enum.Font.GothamBold
        label(row, string.format("%d/%d  •  %s", participant.score, 9, result), UDim2.fromOffset(180, 20), UDim2.fromOffset(10, 29), resultColor, 11)

        local jjCountBox = textBox(row, "JJs", UDim2.fromOffset(50, 26), UDim2.fromOffset(195, 7))
        jjCountBox.Text = participant.jjCount
        jjCountBox.FocusLost:Connect(function()
            participant.jjCount = jjCountBox.Text
        end)

        local jjTimer = participant.timers.JJ
        local jjText = jjTimer and jjTimer.elapsed and ("JJ " .. formatSeconds(jjTimer.elapsed)) or (jjTimer and "JJ parar" or "JJ iniciar")
        addSmallButton(row, jjText, 250, 83, function()
            toggleTimer(participant, "JJ", rules.jjTime)
        end, COLORS.accent)

        local x = 339
        for p = 1, 4 do
            local key = "P" .. p
            local timer = participant.timers[key]
            local text = timer and timer.elapsed and ("P" .. p .. " " .. formatSeconds(timer.elapsed)) or (timer and ("P" .. p .. " parar") or ("P" .. p .. " iniciar"))
            addSmallButton(row, text, x, 82, function()
                toggleTimer(participant, key, parkourLimits[p])
            end)
            x += 87
        end

        local textPoints = participant.awards.TEXT
        addSmallButton(row, "Texto " .. textPoints .. "p", 195, 83, function()
            setTextPoints(participant, nil)
        end, COLORS.orange)

        local textErrorsBox = textBox(row, "erros", UDim2.fromOffset(58, 26), UDim2.fromOffset(285, 40))
        textErrorsBox.Text = participant.textErrors
        textErrorsBox.FocusLost:Connect(function()
            participant.textErrors = textErrorsBox.Text
        end)

        addSmallButton(row, "Pergunta ✓", 349, 88, function()
            setQuestionPoints(participant, true)
        end, COLORS.accent)
        addSmallButton(row, "Pergunta 0", 442, 82, function()
            setQuestionPoints(participant, false)
        end, COLORS.red)

        addSmallButton(row, "Remover", 529, 78, function()
            for i, item in ipairs(participants) do
                if item.id == participant.id then
                    table.remove(participants, i)
                    break
                end
            end
            refreshRows()
        end, COLORS.red)
        addSmallButton(row, participant.textTheme and "Tema OK" or "Fora do tema", 614, 100, function()
            participant.textTheme = not participant.textTheme
            refreshRows()
        end, participant.textTheme and COLORS.accent or COLORS.red)

        label(row, string.format("Limites: JJ %ds | P1 %ds | P2 %ds | P3 %ds | P4 %ds | Textos: erros 0=2p, 1-3=1p, >3=0p", rules.jjTime, parkourLimits[1], parkourLimits[2], parkourLimits[3], parkourLimits[4]), UDim2.new(1, -20, 0, 19), UDim2.fromOffset(10, 73), COLORS.muted, 10)
    end
end

local function addParticipant()
    local name = participantBox.Text:gsub("^%s+", ""):gsub("%s+$", "")
    if name == "" then
        output.Text = "Digite o nome do participante antes de adicionar."
        return
    end
    table.insert(participants, makeParticipant(name))
    participantBox.Text = ""
    refreshRows()
end

button(addPanel, "Adicionar", UDim2.fromOffset(95, 30), UDim2.fromOffset(430, 6), addParticipant, COLORS.accent)
participantBox.FocusLost:Connect(function(enterPressed)
    if enterPressed then
        addParticipant()
    end
end)

local function generateAnnouncement()
    local instructor = instructorBox.Text ~= "" and instructorBox.Text or "(sua marcação)"
    local auxiliaries = auxiliariesBox.Text ~= "" and auxiliariesBox.Text or "(apenas Oficiais)"
    local schedule = timeBox.Text ~= "" and timeBox.Text or "(00:00)"
    local serverCode = serverBox.Text ~= "" and serverBox.Text or "(gerado no jogo)"
    local amount = amountBox.Text ~= "" and amountBox.Text or "01/50"

    output.Text = string.format([[TREINAMENTO FÍSICO (%s)
◈─────────────────────────◈
| • Instrutor: %s
| • Auxiliares: %s
| • Patente do Instrutor: Aspirante a Oficial ou acima
| • Patente dos Auxiliares: Aspirante a Oficial ou acima
◈─────────────────────────◈
| • Marcação: %s
◈─────────────────────────◈
| • Horário: %s
| • Código do Servidor: %s
◈─────────────────────────◈
→ Observações e Normas ←
1 - Formar fila no STS e aguardar em silêncio.
2 - Para falar, usar PPF e aguardar autorização.
3 - Brigas ou discussões não serão toleradas.
4 - Atrasados dependem da autorização do instrutor.
5 - Burlas de comandos ou instruções podem gerar penalidade.
6 - Não questionar o resultado durante o treinamento.
7 - Manter postura, disciplina, respeito e organização.
8 - O instrutor decidirá sobre a entrada de atrasados.]], amount, instructor, auxiliaries, role, schedule, serverCode)
end

local function generateReport()
    local approved = {}
    local failed = {}
    local instructor = instructorBox.Text ~= "" and instructorBox.Text or "(sua marcação)"
    local auxiliaries = auxiliariesBox.Text ~= "" and auxiliariesBox.Text or "(apenas oficiais)"

    for _, participant in ipairs(participants) do
        if participant.score >= currentRules().pass then
            table.insert(approved, string.format("%s - %d/%d pontos", participant.name, participant.score, 9))
        else
            table.insert(failed, string.format("%s - %d/%d pontos", participant.name, participant.score, 9))
        end
    end

    output.Text = string.format([[RELATÓRIO DE PROMOÇÃO (01)
◈─────────────────────────◈
Instrutor: %s
Auxiliares: %s
Perfil: %s

Aprovados (mínimo %d pontos):
%s

Reprovados:
%s

Data e hora: %s
Observações: Avaliação registrada pelo painel do instrutor.
Comprovações: anexar fotos obrigatórias.
◈─────────────────────────◈
Lembrete: promover os aprovados no site oficial dentro de 6 horas e enviar o relatório no canal correto.]],
        instructor,
        auxiliaries,
        role,
        currentRules().pass,
        #approved > 0 and table.concat(approved, "\n") or "(nenhum)",
        #failed > 0 and table.concat(failed, "\n") or "(nenhum)",
        os.date("%d/%m/%Y %H:%M"))
end

button(main, "Gerar anúncio", UDim2.fromOffset(120, 30), UDim2.fromOffset(12, 622), generateAnnouncement, COLORS.accent)
button(main, "Gerar relatório", UDim2.fromOffset(120, 30), UDim2.fromOffset(140, 622), generateReport, COLORS.orange)
button(main, "Limpar saída", UDim2.fromOffset(105, 30), UDim2.fromOffset(268, 622), function()
    output.Text = ""
end, COLORS.panel2)
label(main, "Os comandos ;h, ;countdown, ;title, ;kick e ;clogs devem ser usados manualmente pelo instrutor autorizado.", UDim2.new(1, -400, 0, 30), UDim2.fromOffset(390, 622), COLORS.muted, 10)

refreshMeta()
refreshRows()
