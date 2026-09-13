-- TREINAMENTO FÍSICO • WINDUI
-- Painel manual para uma experiência autorizada.
-- Requer um ModuleScript chamado "WindUI" em ReplicatedStorage.
-- Coloque este LocalScript em StarterPlayer > StarterPlayerScripts.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local WindUI = require(
    ReplicatedStorage:WaitForChild("WindUI")
)

-- =========================================================
-- REGRAS OFICIAIS DO DOCUMENTO
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

        tower = {
            ["PC e CONSOLE"] = 15,
            ["CELULAR"] = 16,
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
            D = {27, 25, 30, 30},
        },

        tower = {
            ["PC e CONSOLE"] = 15,
            ["CELULAR"] = 16,
        },
    },
}

-- =========================================================
-- ESTADO
-- =========================================================

local state = {
    role = "Praças",
    version = "A",
    device = "PC e CONSOLE",

    participants = {},
    nextId = 0,

    rankNick = "",
    rankPoints = "",
}

-- =========================================================
-- CORES
-- =========================================================

local GREEN = Color3.fromHex("#31C46B")
local BLUE = Color3.fromHex("#3D82F6")
local ORANGE = Color3.fromHex("#E29A3B")
local RED = Color3.fromHex("#E24B4B")
local GRAY = Color3.fromHex("#8C93A1")

-- =========================================================
-- FUNÇÕES
-- =========================================================

local function notify(title, content, icon)
    WindUI:Notify({
        Title = title,
        Content = content,
        Icon = icon or "info",
        Duration = 3,
    })
end

local function trim(value)
    return tostring(value or "")
        :gsub("^%s+", "")
        :gsub("%s+$", "")
end

local function newParticipant(name)
    state.nextId += 1

    return {
        id = state.nextId,
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

local function award(participant, key, points)
    participant.score -= participant.awards[key] or 0
    participant.awards[key] = math.max(0, points)
    participant.score += participant.awards[key]
end

local function startOrStopTimer(participant, key, limit, onFinish)
    local timer = participant.timers[key]

    if not timer then
        participant.timers[key] = {
            started = os.clock(),
        }

        notify(
            "Cronômetro iniciado",
            participant.name .. " • " .. key,
            "play"
        )

        return
    end

    if timer.elapsed then
        notify(
            "Cronômetro finalizado",
            key .. " • " .. timer.elapsed .. "s",
            "timer"
        )
        return
    end

    timer.elapsed = math.floor(
        os.clock() - timer.started + 0.5
    )

    local passed = timer.elapsed <= limit

    if onFinish then
        onFinish(passed, timer.elapsed)
    end
end

local function getStatus(participant)
    local required = RULES[state.role].pass

    if participant.score >= required then
        return "APROVADO"
    end

    return "EM AVALIAÇÃO"
end

local function getTimerTitle(participant, key)
    local timer = participant.timers[key]

    if not timer then
        return key .. " • Iniciar"
    end

    if not timer.elapsed then
        local elapsed = math.floor(
            os.clock() - timer.started + 0.5
        )

        return key .. " • " .. elapsed .. "s • Parar"
    end

    return key .. " • " .. timer.elapsed .. "s"
end

-- =========================================================
-- WINDOW WINDUI
-- =========================================================

local Window = WindUI:CreateWindow({
    Title = "TREINAMENTO FÍSICO",
    Icon = "clipboard-check",
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
            Color3.fromHex("#31C46B"),
            Color3.fromHex("#3D82F6")
        ),
    },
})

Window:Tag({
    Title = "WINDUI",
    Icon = "layers",
    Color = GREEN,
    Border = true,
})

-- =========================================================
-- TABS
-- =========================================================

local EvaluationTab = Window:Tab({
    Title = "Avaliação",
    Desc = "Avaliação dos participantes",
    Icon = "clipboard-check",
    IconColor = GREEN,
    IconShape = "Square",
    Border = true,
})

local RankTab = Window:Tab({
    Title = "Patente",
    Desc = "Entrega de pontos",
    Icon = "medal",
    IconColor = ORANGE,
    IconShape = "Square",
    Border = true,
})

local HelpTab = Window:Tab({
    Title = "Ajuda",
    Desc = "Regras do treinamento",
    Icon = "info",
    IconColor = BLUE,
    IconShape = "Square",
    Border = true,
})

-- =========================================================
-- AVALIAÇÃO • CONFIGURAÇÃO
-- =========================================================

EvaluationTab:Section({
    Title = "CONFIGURAÇÃO DA AVALIAÇÃO",
    TextSize = 18,
    Opened = true,
})

local roleDropdown = EvaluationTab:Dropdown({
    Title = "Patente",
    Desc = "Selecione Praças ou Graduados",
    Values = {"Praças", "Graduados"},
    Value = state.role,

    Callback = function(value)
        state.role = value
        refreshParticipants()
        updateRules()
    end,
})

local versionDropdown = EvaluationTab:Dropdown({
    Title = "Versão do Parkour",
    Desc = "A, B, C ou D",
    Values = {"A", "B", "C", "D"},
    Value = state.version,

    Callback = function(value)
        state.version = value
        refreshParticipants()
        updateRules()
    end,
})

local deviceDropdown = EvaluationTab:Dropdown({
    Title = "Torre",
    Desc = "Dispositivo utilizado",
    Values = {"PC e CONSOLE", "CELULAR"},
    Value = state.device,

    Callback = function(value)
        state.device = value
        updateRules()
    end,
})

local rulesParagraph = EvaluationTab:Paragraph({
    Title = "Regras atuais",
    Desc = "",
})

function updateRules()
    local rules = RULES[state.role]
    local parkours = rules.parkours[state.version]
    local towerTime = rules.tower[state.device]

    rulesParagraph:SetDesc(string.format(
        "%s\n\nJJ: %d em %ds\n" ..
        "P1: %ds • P2: %ds • P3: %ds • P4: %ds\n" ..
        "Torre: %ds\n" ..
        "Mínimo para aprovação: %d pontos",
        state.role,
        rules.jj,
        rules.jjTime,
        parkours[1],
        parkours[2],
        parkours[3],
        parkours[4],
        towerTime,
        rules.pass
    ))
end

-- =========================================================
-- PARTICIPANTES
-- =========================================================

EvaluationTab:Section({
    Title = "ADICIONAR PARTICIPANTE",
    TextSize = 18,
    Opened = true,
})

local pendingName = ""

EvaluationTab:Input({
    Title = "Nome",
    Desc = "Nome/Nick do participante",
    Placeholder = "Digite o nome...",
    InputIcon = "user",
    Callback = function(value)
        pendingName = trim(value)
    end,
})

EvaluationTab:Button({
    Title = "Adicionar participante",
    Desc = "Adicionar à lista de avaliação",
    Icon = "user-plus",
    Color = GREEN,

    Callback = function()
        if pendingName == "" then
            notify(
                "Nome vazio",
                "Digite o nome do participante.",
                "circle-alert"
            )
            return
        end

        table.insert(
            state.participants,
            newParticipant(pendingName)
        )

        pendingName = ""

        refreshParticipants()

        notify(
            "Participante adicionado",
            "O participante foi adicionado à avaliação.",
            "circle-check"
        )
    end,
})

local participantSections = {}

function clearParticipantSections()
    for _, section in ipairs(participantSections) do
        pcall(function()
            section:Destroy()
        end)
    end

    table.clear(participantSections)
end

function refreshParticipants()
    clearParticipantSections()

    if #state.participants == 0 then
        local empty = EvaluationTab:Section({
            Title = "PARTICIPANTES",
            Box = true,
            Opened = true,
        })

        empty:Paragraph({
            Title = "Nenhum participante",
            Desc = "Adicione um participante acima para começar.",
        })

        table.insert(participantSections, empty)
        return
    end

    local rules = RULES[state.role]
    local limits = rules.parkours[state.version]

    for _, participant in ipairs(state.participants) do
        local section = EvaluationTab:Section({
            Title = participant.name,
            Desc = string.format(
                "%d/9 • %s",
                participant.score,
                getStatus(participant)
            ),
            Box = true,
            Opened = true,
        })

        table.insert(participantSections, section)

        section:Paragraph({
            Title = "Pontuação",
            Desc = string.format(
                "Total: %d/9\n" ..
                "JJ: %d • P1: %d • P2: %d • P3: %d • P4: %d\n" ..
                "Texto: %d • Pergunta: %d",
                participant.score,
                participant.awards.JJ,
                participant.awards.P1,
                participant.awards.P2,
                participant.awards.P3,
                participant.awards.P4,
                participant.awards.TEXT,
                participant.awards.QUESTION
            ),
        })

        section:Input({
            Title = "JJs feitos",
            Desc = string.format(
                "Meta: %d JJs • limite: %ds",
                rules.jj,
                rules.jjTime
            ),
            Placeholder = "Quantidade de JJs",
            Value = participant.jjCount,
            InputIcon = "activity",

            Callback = function(value)
                participant.jjCount = trim(value)
            end,
        })

        section:Button({
            Title = getTimerTitle(participant, "JJ"),
            Desc = string.format(
                "%d JJs em até %ds",
                rules.jj,
                rules.jjTime
            ),
            Icon = "timer",
            Color = GREEN,

            Callback = function()
                local count = tonumber(participant.jjCount) or 0

                startOrStopTimer(
                    participant,
                    "JJ",
                    rules.jjTime,

                    function(passed, elapsed)
                        award(
                            participant,
                            "JJ",
                            passed and count >= rules.jj and 1 or 0
                        )

                        notify(
                            passed and count >= rules.jj
                                and "JJ aprovado"
                                or "JJ não aprovado",

                            string.format(
                                "%s • %d JJs • %ds",
                                participant.name,
                                count,
                                elapsed
                            ),

                            passed and count >= rules.jj
                                and "circle-check"
                                or "circle-x"
                        )
                    end
                )

                refreshParticipants()
            end,
        })

        for parkour = 1, 4 do
            local key = "P" .. parkour
            local limit = limits[parkour]

            section:Button({
                Title = getTimerTitle(participant, key),
                Desc = "Limite: " .. limit .. " segundos",
                Icon = "timer",

                Callback = function()
                    startOrStopTimer(
                        participant,
                        key,
                        limit,

                        function(passed, elapsed)
                            award(
                                participant,
                                key,
                                passed and 1 or 0
                            )

                            notify(
                                passed
                                    and "Parkour aprovado"
                                    or "Parkour não aprovado",

                                string.format(
                                    "%s • %s • %ds",
                                    participant.name,
                                    key,
                                    elapsed
                                ),

                                passed
                                    and "circle-check"
                                    or "circle-x"
                            )
                        end
                    )

                    refreshParticipants()
                end,
            })
        end

        section:Input({
            Title = "Erros gramaticais",
            Desc = "0 = 2 pontos • 1-3 = 1 ponto • +3 = 0",
            Placeholder = "Quantidade de erros",
            Value = participant.textErrors,
            InputIcon = "file-text",

            Callback = function(value)
                participant.textErrors = trim(value)
            end,
        })

        section:Button({
            Title = "Calcular texto",
            Desc = "Aplicar a pontuação gramatical",
            Icon = "calculator",
            Color = ORANGE,

            Callback = function()
                local errors =
                    tonumber(participant.textErrors) or 99

                local points = 0

                if participant.theme and errors == 0 then
                    points = 2
                elseif participant.theme and errors <= 3 then
                    points = 1
                end

                award(
                    participant,
                    "TEXT",
                    points
                )

                refreshParticipants()

                notify(
                    "Texto avaliado",
                    participant.name
                        .. " recebeu "
                        .. points
                        .. " ponto(s).",
                    "file-check"
                )
            end,
        })

        section:Button({
            Title = "Remover participante",
            Icon = "trash-2",
            Color = RED,

            Callback = function()
                for index, item in ipairs(state.participants) do
                    if item.id == participant.id then
                        table.remove(
                            state.participants,
                            index
                        )
                        break
                    end
                end

                refreshParticipants()

                notify(
                    "Participante removido",
                    participant.name .. " foi removido.",
                    "trash-2"
                )
            end,
        })
    end
end

-- =========================================================
-- PATENTE
-- =========================================================

RankTab:Section({
    Title = "ENTREGA DE PONTOS",
    TextSize = 18,
    Opened = true,
})

RankTab:Paragraph({
    Title = "Preparação manual",
    Desc = "Confira o Nick e a quantidade de pontos antes da entrega.",
})

RankTab:Input({
    Title = "Nick",
    Placeholder = "Nick exato",
    InputIcon = "user",

    Callback = function(value)
        state.rankNick = trim(value)
    end,
})

RankTab:Input({
    Title = "Pontos",
    Placeholder = "Ex.: 5",
    InputIcon = "star",

    Callback = function(value)
        state.rankPoints =
            trim(value):gsub("%D", "")
    end,
})

local commandOutput = RankTab:Input({
    Title = "Comando preparado",
    Type = "Textarea",
    Placeholder = "O comando aparecerá aqui...",
    InputIcon = "terminal",
})

RankTab:Button({
    Title = "Preparar comando",
    Icon = "terminal",
    Color = GREEN,

    Callback = function()
        if state.rankNick == ""
            or state.rankPoints == "" then

            commandOutput:Set(
                "Preencha Nick e pontos."
            )

            notify(
                "Campos incompletos",
                "Informe Nick e pontos.",
                "circle-alert"
            )

            return
        end

        local command =
            ";titler "
            .. state.rankNick
            .. " "
            .. state.rankPoints

        commandOutput:Set(command)

        notify(
            "Comando preparado",
            "Confira o comando antes da utilização.",
            "circle-check"
        )
    end,
})

-- =========================================================
-- AJUDA
-- =========================================================

HelpTab:Section({
    Title = "COMO USAR",
    TextSize = 18,
    Opened = true,
})

HelpTab:Paragraph({
    Title = "Avaliação",
    Desc =
        "1. Escolha a patente.\n" ..
        "2. Escolha a versão.\n" ..
        "3. Escolha a torre.\n" ..
        "4. Adicione os participantes.\n" ..
        "5. Faça as avaliações e cronômetros.\n" ..
        "6. Confira a pontuação final.",
})

HelpTab:Section({
    Title = "CRITÉRIOS",
    TextSize = 18,
    Opened = true,
})

HelpTab:Paragraph({
    Title = "Praças",
    Desc =
        "JJ: 150 em 210s.\n" ..
        "Mínimo para aprovação: 4 pontos.",
})

HelpTab:Paragraph({
    Title = "Graduados",
    Desc =
        "JJ: 170 em 230s.\n" ..
        "Mínimo para aprovação: 5 pontos.",
})

HelpTab:Paragraph({
    Title = "Texto gramatical",
    Desc =
        "400 segundos.\n" ..
        "0 erros = 2 pontos.\n" ..
        "1 a 3 erros = 1 ponto.\n" ..
        "Mais de 3 erros = 0 pontos.",
})

HelpTab:Paragraph({
    Title = "Parkours",
    Desc =
        "Cada parkour vale 1 ponto.\n" ..
        "Os tempos são alterados automaticamente " ..
        "conforme patente e versão selecionadas.",
})

HelpTab:Section({
    Title = "TORRE",
    TextSize = 18,
    Opened = true,
})

HelpTab:Paragraph({
    Title = "Tempos",
    Desc =
        "PC e CONSOLE: 15 segundos.\n" ..
        "CELULAR: 16 segundos.",
})

HelpTab:Section({
    Title = "PERGUNTAS",
    TextSize = 18,
    Opened = true,
})

HelpTab:Paragraph({
    Title = "Avaliação manual",
    Desc =
        "1 pergunta vale 1 ponto.\n" ..
        "O instrutor deve conferir a resposta manualmente.\n" ..
        "O timer indicado no documento é de 40 segundos.",
})

-- =========================================================
-- INICIALIZAÇÃO
-- =========================================================

updateRules()
refreshParticipants()

notify(
    "Treinamento Físico",
    "WindUI carregado com sucesso.",
    "circle-check"
)
