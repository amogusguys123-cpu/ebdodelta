--[[
    TREINAMENTO FÍSICO - WINDUI
    Migração da interface do painel original para WindUI.

    Instalação recomendada para Roblox Studio:
    1. Coloque o ModuleScript "WindUI" em ReplicatedStorage.
    2. Coloque este arquivo como LocalScript em:
       StarterPlayer > StarterPlayerScripts

    Observação:
    Este painel mantém a lógica manual do sistema original.
    Ele não lê dados ocultos, não executa comandos ao tocar em jogadores
    e não substitui a validação do servidor.
]]

local Players = game:GetService("Players")
local player = Players.LocalPlayer

local WindUI = require(game:GetService("ReplicatedStorage"):WaitForChild("WindUI"))

-- =========================================================
-- REGRAS
-- =========================================================

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

local TOWER_RULES = {
    ["PC/Console"] = 15,
    ["Celular"] = 16,
}

local role = "Praças"
local version = "A"
local device = "PC/Console"

local participants = {}
local nextId = 0

-- =========================================================
-- CORES / UTILITÁRIOS
-- =========================================================

local COLORS = {
    Green = Color3.fromHex("#30C46B"),
    Blue = Color3.fromHex("#4A8DFF"),
    Orange = Color3.fromHex("#E39B3B"),
    Red = Color3.fromHex("#E05252"),
    Gray = Color3.fromHex("#858C99"),
}

local function notify(title, content, icon)
    WindUI:Notify({
        Title = title,
        Content = content,
        Icon = icon or "solar:info-circle-bold",
        Duration = 3,
    })
end

local function clean(value)
    return tostring(value or "")
        :gsub("^%s+", "")
        :gsub("%s+$", "")
end

local function award(participant, key, value)
    participant.score -= participant.awards[key] or 0
    participant.awards[key] = math.max(0, value)
    participant.score += participant.awards[key]
end

local function timerText(participant, key, prefix)
    local timer = participant.timers[key]

    if not timer then
        return prefix .. " • Iniciar"
    end

    if not timer.elapsed then
        local elapsed = math.floor(os.clock() - timer.started + 0.5)
        return string.format("%s • %ds", prefix, elapsed)
    end

    return string.format("%s • %ds", prefix, timer.elapsed)
end

local function calculateText(participant)
    local errors = tonumber(participant.textErrors) or 99
    local points = 0

    if participant.theme and errors == 0 then
        points = 2
    elseif participant.theme and errors <= 3 then
        points = 1
    end

    award(participant, "TEXT", points)
end

local function newParticipant(name)
    nextId += 1

    return {
        id = nextId,
        name = name,
        score = 0,

        awards = {
            JJ = 0,
            P1 = 0,
            P2 = 0,
            P3 = 0,
            P4 = 0,
            TEXT = 0,
            QUESTION = 0,
        },

        timers = {},

        jjCount = "",
        textErrors = "",
        theme = true,
    }
end

-- =========================================================
-- WINDOW
-- =========================================================

local Window = WindUI:CreateWindow({
    Title = "TREINAMENTO FÍSICO",
    Icon = "solar:running-2-bold",
    Folder = "TreinamentoFisico",
    NewElements = true,

    Topbar = {
        Height = 44,
        ButtonsType = "Mac",
    },

    OpenButton = {
        Title = "Abrir Treinamento",
        CornerRadius = UDim.new(1, 0),
        StrokeThickness = 2,
        Enabled = true,
        Draggable = true,
        OnlyMobile = false,
        Scale = 0.55,
        Color = ColorSequence.new(
            COLORS.Green,
            COLORS.Blue
        ),
    },
})

Window:Tag({
    Title = "GUI Mobile",
    Icon = "solar:smartphone-bold",
    Color = COLORS.Green,
    Border = true,
})

-- =========================================================
-- ABAS
-- =========================================================

local EvaluationTab = Window:Tab({
    Title = "Avaliação",
    Desc = "Gerencie os participantes",
    Icon = "solar:clipboard-check-bold",
    IconColor = COLORS.Green,
    IconShape = "Square",
    Border = true,
})

local RankTab = Window:Tab({
    Title = "Patente",
    Desc = "Prepare a entrega de pontos",
    Icon = "solar:medal-star-bold",
    IconColor = COLORS.Orange,
    IconShape = "Square",
    Border = true,
})

local HelpTab = Window:Tab({
    Title = "Ajuda",
    Desc = "Regras e funcionamento",
    Icon = "solar:info-circle-bold",
    IconColor = COLORS.Blue,
    IconShape = "Square",
    Border = true,
})

-- =========================================================
-- AVALIAÇÃO
-- =========================================================

EvaluationTab:Section({
    Title = "Configuração",
    TextSize = 18,
})

local RoleDropdown = EvaluationTab:Dropdown({
    Title = "Patente",
    Desc = "Escolha o grupo da avaliação",
    Values = {"Praças", "Graduados"},
    Value = role,
    Callback = function(value)
        role = value
        notify(
            "Patente alterada",
            role .. " • mínimo " .. RULES[role].pass .. " pontos",
            "solar:shield-user-bold"
        )
    end,
})

local VersionDropdown = EvaluationTab:Dropdown({
    Title = "Parkour",
    Desc = "Escolha a versão do circuito",
    Values = {"A", "B", "C", "D"},
    Value = version,
    Callback = function(value)
        version = value
    end,
})

local DeviceDropdown = EvaluationTab:Dropdown({
    Title = "Torre",
    Desc = "Dispositivo utilizado",
    Values = {"PC/Console", "Celular"},
    Value = device,
    Callback = function(value)
        device = value
    end,
})

EvaluationTab:Section({
    Title = "Regras atuais",
    TextSize = 15,
})

local RulesParagraph = EvaluationTab:Paragraph({
    Title = "Critérios",
    Content = "",
})

local function updateRulesParagraph()
    local rules = RULES[role]
    RulesParagraph:SetContent(
        string.format(
            "%s\n%d JJs em até %ds\nAprovação: %d pontos\nParkour %s • Torre: %s",
            role,
            rules.jj,
            rules.jjTime,
            rules.pass,
            version,
            device
        )
    )
end

updateRulesParagraph()

-- Como as callbacks dos dropdowns são disparadas pelo WindUI,
-- mantemos a atualização também por um pequeno monitor.
task.spawn(function()
    local oldRole = role
    local oldVersion = version
    local oldDevice = device

    while task.wait(0.15) do
        if oldRole ~= role or oldVersion ~= version or oldDevice ~= device then
            oldRole = role
            oldVersion = version
            oldDevice = device
            updateRulesParagraph()
        end
    end
end)

EvaluationTab:Section({
    Title = "Adicionar participante",
    TextSize = 18,
})

local nameInput = EvaluationTab:Input({
    Title = "Nome do participante",
    Desc = "Digite o nome que aparecerá na avaliação",
    Placeholder = "Nome do participante",
    InputIcon = "solar:user-bold",
    Type = "Input",
    Callback = function(value)
        -- O valor é lido pelo botão abaixo.
    end,
})

EvaluationTab:Button({
    Title = "Adicionar participante",
    Desc = "Cria um novo cartão de avaliação",
    Icon = "solar:user-plus-bold",
    Color = COLORS.Green,
    Callback = function()
        local name = clean(nameInput:Get())

        if name == "" then
            notify("Atenção", "Digite o nome do participante.", "solar:danger-circle-bold")
            return
        end

        table.insert(participants, newParticipant(name))
        nameInput:Set("")

        notify(
            "Participante adicionado",
            name .. " foi adicionado à avaliação.",
            "solar:check-circle-bold"
        )
    end,
})

-- =========================================================
-- CARDS DOS PARTICIPANTES
-- =========================================================

EvaluationTab:Section({
    Title = "Participantes",
    TextSize = 18,
})

local function getParticipantDescription(participant)
    local rules = RULES[role]
    local status = participant.score >= rules.pass and "APROVADO" or "EM AVALIAÇÃO"

    return string.format(
        "%d/9 pontos • %s\nJJ: %d • Texto: %d",
        participant.score,
        status,
        participant.awards.JJ or 0,
        participant.awards.TEXT or 0
    )
end

local function makeParticipantSection(participant)
    local rules = RULES[role]
    local limits = rules.parkours[version]
    local towerLimit = TOWER_RULES[device]

    local section = EvaluationTab:Section({
        Title = participant.name,
        Desc = getParticipantDescription(participant),
        Box = true,
        BoxBorder = true,
        Opened = true,
    })

    section:Paragraph({
        Title = "Status",
        Content = getParticipantDescription(participant),
    })

    section:Paragraph({
        Title = "Tempos oficiais",
        Content = string.format(
            "P1: %ds • P2: %ds • P3: %ds • P4: %ds\\nTorre (%s): %ds",
            limits[1], limits[2], limits[3], limits[4],
            device, towerLimit
        ),
    })

    section:Input({
        Title = "JJs feitos",
        Desc = string.format(
            "Meta: %d JJs • limite: %ds",
            rules.jj,
            rules.jjTime
        ),
        Placeholder = "Ex.: 150",
        Value = participant.jjCount,
        InputIcon = "solar:running-2-bold",
        Callback = function(value)
            participant.jjCount = clean(value)
        end,
    })

    section:Button({
        Title = timerText(participant, "JJ", "JJ"),
        Icon = "solar:stopwatch-bold",
        Color = COLORS.Green,
        Callback = function()
            local count = tonumber(participant.jjCount) or 0
            local timer = participant.timers.JJ

            if not timer then
                participant.timers.JJ = {
                    started = os.clock(),
                }

                notify(
                    "JJ iniciado",
                    participant.name .. " • cronômetro iniciado.",
                    "solar:play-bold"
                )

            elseif not timer.elapsed then
                timer.elapsed = math.floor(
                    os.clock() - timer.started + 0.5
                )

                local passed =
                    timer.elapsed <= rules.jjTime
                    and count >= rules.jj

                award(
                    participant,
                    "JJ",
                    passed and 1 or 0
                )

                notify(
                    passed and "JJ aprovado" or "JJ não aprovado",
                    string.format(
                        "%s • %d JJs • %ds",
                        participant.name,
                        count,
                        timer.elapsed
                    ),
                    passed
                        and "solar:check-circle-bold"
                        or "solar:close-circle-bold"
                )
            end
        end,
    })

    for p = 1, 4 do
        local key = "P" .. p

        section:Button({
            Title = timerText(participant, key, "P" .. p),
            Desc = string.format(
                "Limite: %ds",
                limits[p]
            ),
            Icon = "solar:stopwatch-minimalistic-bold",
            Callback = function()
                local timer = participant.timers[key]

                if not timer then
                    participant.timers[key] = {
                        started = os.clock(),
                    }

                    notify(
                        "P" .. p .. " iniciado",
                        participant.name .. " • cronômetro iniciado.",
                        "solar:play-bold"
                    )

                elseif not timer.elapsed then
                    timer.elapsed = math.floor(
                        os.clock() - timer.started + 0.5
                    )

                    local passed =
                        timer.elapsed <= limits[p]

                    award(
                        participant,
                        key,
                        passed and 1 or 0
                    )

                    notify(
                        passed and "Parkour aprovado" or "Parkour não aprovado",
                        string.format(
                            "%s • P%d • %ds",
                            participant.name,
                            p,
                            timer.elapsed
                        ),
                        passed
                            and "solar:check-circle-bold"
                            or "solar:close-circle-bold"
                    )
                end
            end,
        })
    end

    section:Input({
        Title = "Erros no texto",
        Desc = "0 erros = 2 pontos • 1-3 erros = 1 ponto",
        Placeholder = "Ex.: 0",
        Value = participant.textErrors,
        InputIcon = "solar:document-text-bold",
        Callback = function(value)
            participant.textErrors = clean(value)
        end,
    })

    section:Button({
        Title = "Calcular texto",
        Desc = "Atualiza a pontuação do texto",
        Icon = "solar:calculator-bold",
        Color = COLORS.Orange,
        Callback = function()
            calculateText(participant)

            notify(
                "Texto calculado",
                participant.name
                    .. " • "
                    .. tostring(participant.awards.TEXT)
                    .. " ponto(s).",
                "solar:document-check-bold"
            )
        end,
    })

    section:Button({
        Title = "Remover participante",
        Icon = "solar:trash-bin-trash-bold",
        Color = COLORS.Red,
        Callback = function()
            for i, item in ipairs(participants) do
                if item.id == participant.id then
                    table.remove(participants, i)
                    break
                end
            end

            notify(
                "Participante removido",
                participant.name .. " foi removido.",
                "solar:trash-bin-trash-bold"
            )
        end,
    })
end

-- Recria a visualização dos participantes quando solicitado.
-- O WindUI não possui uma API única para limpar todos os elementos
-- de uma Tab em todas as versões; por isso usamos uma aba dedicada
-- de atualização manual e mantemos os dados na tabela.
EvaluationTab:Button({
    Title = "Atualizar painel",
    Desc = "Reconstrói a seção dos participantes",
    Icon = "solar:refresh-bold",
    Callback = function()
        for _, participant in ipairs(participants) do
            makeParticipantSection(participant)
        end

        notify(
            "Painel atualizado",
            tostring(#participants) .. " participante(s).",
            "solar:refresh-bold"
        )
    end,
})

-- =========================================================
-- PATENTE
-- =========================================================

RankTab:Section({
    Title = "Entrega de pontos",
    TextSize = 18,
})

RankTab:Paragraph({
    Title = "Preparação",
    Content = "Confira o Nick e os pontos antes de usar o comando.",
})

local rankNick = ""
local rankAmount = ""
local rankCommand = ""

RankTab:Input({
    Title = "Nick exato",
    Placeholder = "Digite o Nick",
    InputIcon = "solar:user-bold",
    Callback = function(value)
        rankNick = clean(value)
    end,
})

RankTab:Input({
    Title = "Pontos",
    Placeholder = "Ex.: 5",
    InputIcon = "solar:star-bold",
    Callback = function(value)
        rankAmount = clean(value):gsub("%D", "")
    end,
})

local CommandOutput = RankTab:Input({
    Title = "Comando preparado",
    Desc = "Use para conferir/copiar manualmente",
    Placeholder = "O comando aparecerá aqui",
    Type = "Textarea",
    Value = "",
    Callback = function(value)
        rankCommand = value
    end,
})

RankTab:Button({
    Title = "Preparar comando",
    Icon = "solar:command-bold",
    Color = COLORS.Green,
    Callback = function()
        if rankNick == "" or rankAmount == "" then
            CommandOutput:Set("Preencha Nick e pontos.")
            notify(
                "Campos incompletos",
                "Informe o Nick e a quantidade de pontos.",
                "solar:danger-circle-bold"
            )
            return
        end

        rankCommand = ";titler " .. rankNick .. " " .. rankAmount
        CommandOutput:Set(rankCommand)

        notify(
            "Comando preparado",
            "Confira o comando antes de usar.",
            "solar:check-circle-bold"
        )
    end,
})

RankTab:Button({
    Title = "Selecionar comando",
    Desc = "Coloca o cursor no campo para seleção manual",
    Icon = "solar:copy-bold",
    Callback = function()
        if rankCommand == "" then
            notify(
                "Nada para selecionar",
                "Primeiro prepare o comando.",
                "solar:info-circle-bold"
            )
            return
        end

        CommandOutput:Set(rankCommand)

        notify(
            "Comando pronto",
            "Selecione/copiar manualmente pelo campo.",
            "solar:copy-bold"
        )
    end,
})

-- =========================================================
-- AJUDA
-- =========================================================

HelpTab:Section({
    Title = "Como usar",
    TextSize = 18,
})

HelpTab:Paragraph({
    Title = "Passo a passo",
    Content = [[
1. Em Avaliação, escolha Praças ou Graduados.
2. Escolha a versão do parkour.
3. Escolha o dispositivo da torre.
4. Adicione cada participante.
5. Informe a quantidade de JJs.
6. Inicie e pare os cronômetros.
7. Informe os erros do texto.
8. Calcule a pontuação do texto.
9. Confira a aba Patente para preparar a entrega.
]],
})

HelpTab:Section({
    Title = "Critérios",
    TextSize = 18,
})

HelpTab:Paragraph({
    Title = "Praças",
    Content = "150 JJs em até 210 segundos. Mínimo: 4 pontos.",
})

HelpTab:Paragraph({
    Title = "Graduados",
    Content = "170 JJs em até 230 segundos. Mínimo: 5 pontos.",
})

HelpTab:Paragraph({
    Title = "Texto",
    Content = "0 erros = 2 pontos; 1 a 3 erros = 1 ponto; mais de 3 = 0 pontos. Fugir do tema = 0 pontos.",
})

HelpTab:Paragraph({
    Title = "Parkours",
    Content = "Praças: A 35/40/30/32s • B 30/35/30/28s • C 30/35/35/40s • D 35/30/30/40s. Graduados: A 30/35/27/29s • B 27/30/27/25s • C 25/27/27/30s • D 27/25/25/30s. Torre: 15s PC/Console e 16s Celular. Cada parkour vale 1 ponto.",
})

HelpTab:Section({
    Title = "Observação",
    TextSize = 18,
})

HelpTab:Paragraph({
    Title = "Uso autorizado",
    Content = "O painel é manual e não substitui a validação do servidor.",
})

notify(
    "Treinamento Físico",
    "Painel WindUI carregado.",
    "solar:check-circle-bold"
)
