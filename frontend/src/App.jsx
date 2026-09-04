import { useState, useEffect } from "react"

const API_URL = "http://127.0.0.1:8000"

function App() {
  // ==================================================
  // AUTHENTICATION
  // ==================================================

  const [isRegister, setIsRegister] = useState(false)

  const [isLoggedIn, setIsLoggedIn] = useState(
    Boolean(localStorage.getItem("access_token"))
  )

  const [fullName, setFullName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  // ==================================================
  // DASHBOARD
  // ==================================================

  const [stats, setStats] = useState({
    engagements: 0,
    findings: 0,
    evidence: 0,
  })

  const [dashboardLoading, setDashboardLoading] =
    useState(false)

  const [dashboardError, setDashboardError] =
    useState("")

  // ==================================================
  // ENGAGEMENTS
  // ==================================================

  const [engagements, setEngagements] =
    useState([])

  const [engagementsLoading, setEngagementsLoading] =
    useState(false)

  const [engagementsError, setEngagementsError] =
    useState("")

  const [showCreateEngagement, setShowCreateEngagement] =
    useState(false)

  const [engagementName, setEngagementName] =
    useState("")

  const [clientName, setClientName] =
    useState("")

  const [startDate, setStartDate] =
    useState("")

  const [endDate, setEndDate] =
    useState("")

  const [scope, setScope] =
    useState("")

  const [engagementStatus, setEngagementStatus] =
    useState("active")

  const [creatingEngagement, setCreatingEngagement] =
    useState(false)

  // ==================================================
  // ENGAGEMENT WORKSPACE
  // ==================================================

  const [selectedEngagementId, setSelectedEngagementId] =
    useState(null)

  const [selectedEngagement, setSelectedEngagement] =
    useState(null)

  const [selectedFindings, setSelectedFindings] =
    useState([])

  const [
    engagementWorkspaceLoading,
    setEngagementWorkspaceLoading,
  ] = useState(false)

  const [
    engagementWorkspaceError,
    setEngagementWorkspaceError,
  ] = useState("")

  // ==================================================
  // DISCOVERY
  // ==================================================

  const [showDiscovery, setShowDiscovery] =
    useState(false)

  const [discoveryId, setDiscoveryId] =
    useState(null)

  const [discoveryType, setDiscoveryType] =
    useState("")

  const [discoveryUrl, setDiscoveryUrl] =
    useState("")

  const [discoveryParameter, setDiscoveryParameter] =
    useState("")

  const [discoveryNotes, setDiscoveryNotes] =
    useState("")

  const [discoveryEvidence, setDiscoveryEvidence] =
    useState("")

  const [discoveryEvidenceType, setDiscoveryEvidenceType] =
    useState("note")

  const [analyzingDiscovery, setAnalyzingDiscovery] =
    useState(false)

  // ==================================================
  // GENERATED FINDING
  // ==================================================

  const [generatedFinding, setGeneratedFinding] =
    useState(null)

  const [
    savingGeneratedFinding,
    setSavingGeneratedFinding,
  ] = useState(false)

  // ==================================================
  // REGISTER
  // ==================================================

  const handleRegister = async (event) => {
    event.preventDefault()

    setMessage("")
    setError("")

    if (!fullName.trim()) {
      setError(
        "Please enter your full name."
      )
      return
    }

    if (!email.trim()) {
      setError(
        "Please enter your email."
      )
      return
    }

    if (password.length < 8) {
      setError(
        "Password must be at least 8 characters."
      )
      return
    }

    setLoading(true)

    try {
      const response = await fetch(
        `${API_URL}/auth/register`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            full_name:
              fullName.trim(),

            email:
              email.trim(),

            password,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Registration failed."
        )
      }

      setMessage(
        "Account created successfully! You can now login."
      )

      setFullName("")
      setEmail("")
      setPassword("")

    } catch (err) {
      setError(
        err.message ||
          "Registration failed."
      )

    } finally {
      setLoading(false)
    }
  }

  // ==================================================
  // LOGIN
  // ==================================================

  const handleLogin = async (event) => {
    event.preventDefault()

    setMessage("")
    setError("")

    if (!email.trim()) {
      setError(
        "Please enter your email."
      )
      return
    }

    if (!password) {
      setError(
        "Please enter your password."
      )
      return
    }

    setLoading(true)

    try {
      const response = await fetch(
        `${API_URL}/auth/login`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            email:
              email.trim(),

            password,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Invalid email or password."
        )
      }

      if (!data.access_token) {
        throw new Error(
          "Login succeeded but no access token was returned."
        )
      }

      localStorage.setItem(
        "access_token",
        data.access_token
      )

      setPassword("")
      setError("")
      setMessage("")
      setIsLoggedIn(true)

    } catch (err) {
      setError(
        err.message ||
          "Login failed."
      )

    } finally {
      setLoading(false)
    }
  }

  // ==================================================
  // LOAD DASHBOARD
  // ==================================================

  const loadDashboard = async () => {
    const token =
      localStorage.getItem(
        "access_token"
      )

    if (!token) {
      setIsLoggedIn(false)
      return
    }

    setDashboardLoading(true)
    setDashboardError("")

    try {
      const response = await fetch(
        `${API_URL}/dashboard/stats`,
        {
          method: "GET",

          headers: {
            Authorization:
              `Bearer ${token}`,
          },
        }
      )

      const data =
        await response.json()

      if (!response.ok) {
        if (
          response.status === 401
        ) {
          localStorage.removeItem(
            "access_token"
          )

          setIsLoggedIn(false)

          setError(
            "Your session has expired. Please login again."
          )

          return
        }

        throw new Error(
          data.detail ||
            "Failed to load dashboard statistics."
        )
      }

      setStats({
        engagements:
          data.engagements ?? 0,

        findings:
          data.findings ?? 0,

        evidence:
          data.evidence ?? 0,
      })

    } catch (err) {
      console.error(
        "Failed to load dashboard:",
        err
      )

      setDashboardError(
        err.message ||
          "Failed to load dashboard."
      )

    } finally {
      setDashboardLoading(false)
    }
  }

  // ==================================================
  // LOAD ENGAGEMENTS
  // ==================================================

  const loadEngagements =
    async () => {
      const token =
        localStorage.getItem(
          "access_token"
        )

      if (!token) {
        return
      }

      setEngagementsLoading(true)
      setEngagementsError("")

      try {
        const response =
          await fetch(
            `${API_URL}/engagements`,
            {
              method: "GET",

              headers: {
                Authorization:
                  `Bearer ${token}`,
              },
            }
          )

        const data =
          await response.json()

        if (!response.ok) {
          if (
            response.status === 401
          ) {
            localStorage.removeItem(
              "access_token"
            )

            setIsLoggedIn(false)

            setError(
              "Your session has expired. Please login again."
            )

            return
          }

          throw new Error(
            data.detail ||
              "Failed to load engagements."
          )
        }

        setEngagements(
          data.engagements ||
            []
        )

      } catch (err) {
        console.error(
          "Failed to load engagements:",
          err
        )

        setEngagementsError(
          err.message ||
            "Failed to load engagements."
        )

      } finally {
        setEngagementsLoading(
          false
        )
      }
    }

  // ==================================================
  // LOAD ENGAGEMENT WORKSPACE
  // ==================================================

  const loadEngagementWorkspace =
    async (engagementId) => {
      const token =
        localStorage.getItem(
          "access_token"
        )

      if (!token) {
        setIsLoggedIn(false)
        return
      }

      setSelectedEngagementId(
        engagementId
      )

      setSelectedEngagement(null)
      setSelectedFindings([])

      setEngagementWorkspaceLoading(
        true
      )

      setEngagementWorkspaceError(
        ""
      )

      setMessage("")
      setError("")

      try {
        const response =
          await fetch(
            `${API_URL}/engagements/${engagementId}`,
            {
              method: "GET",

              headers: {
                Authorization:
                  `Bearer ${token}`,
              },
            }
          )

        const data =
          await response.json()

        if (!response.ok) {
          if (
            response.status === 401
          ) {
            localStorage.removeItem(
              "access_token"
            )

            setIsLoggedIn(false)

            setError(
              "Your session has expired. Please login again."
            )

            return
          }

          throw new Error(
            data.detail ||
              "Failed to load engagement."
          )
        }

        setSelectedEngagement(
          data.engagement ||
            null
        )

        setSelectedFindings(
          data.findings ||
            []
        )

      } catch (err) {
        console.error(
          "Failed to load engagement:",
          err
        )

        setEngagementWorkspaceError(
          err.message ||
            "Failed to load engagement."
        )

      } finally {
        setEngagementWorkspaceLoading(
          false
        )
      }
    }

  // ==================================================
  // CREATE ENGAGEMENT
  // ==================================================

  const handleCreateEngagement =
    async (event) => {
      event.preventDefault()

      setMessage("")
      setError("")

      if (!engagementName.trim()) {
        setError(
          "Please enter an engagement name."
        )
        return
      }

      if (!clientName.trim()) {
        setError(
          "Please enter the client name."
        )
        return
      }

      const token =
        localStorage.getItem(
          "access_token"
        )

      if (!token) {
        setIsLoggedIn(false)
        return
      }

      setCreatingEngagement(
        true
      )

      try {
        const response =
          await fetch(
            `${API_URL}/engagements`,
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",

                Authorization:
                  `Bearer ${token}`,
              },

              body: JSON.stringify({
                name:
                  engagementName.trim(),

                client_name:
                  clientName.trim(),

                start_date:
                  startDate ||
                  null,

                end_date:
                  endDate ||
                  null,

                scope:
                  scope.trim() ||
                  null,

                status:
                  engagementStatus,
              }),
            }
          )

        const data =
          await response.json()

        if (!response.ok) {
          if (
            response.status === 401
          ) {
            localStorage.removeItem(
              "access_token"
            )

            setIsLoggedIn(false)

            throw new Error(
              "Your session has expired. Please login again."
            )
          }

          throw new Error(
            data.detail ||
              "Failed to create engagement."
          )
        }

        setEngagementName("")
        setClientName("")
        setStartDate("")
        setEndDate("")
        setScope("")
        setEngagementStatus(
          "active"
        )

        setShowCreateEngagement(
          false
        )

        setMessage(
          "Engagement created successfully."
        )

        await Promise.all([
          loadEngagements(),
          loadDashboard(),
        ])

      } catch (err) {
        setError(
          err.message ||
            "Failed to create engagement."
        )

      } finally {
        setCreatingEngagement(
          false
        )
      }
    }

  // ==================================================
  // RESET DISCOVERY
  // ==================================================

  const resetDiscovery = () => {
    setDiscoveryId(null)

    setDiscoveryType("")
    setDiscoveryUrl("")
    setDiscoveryParameter("")
    setDiscoveryNotes("")
    setDiscoveryEvidence("")

    setDiscoveryEvidenceType(
      "note"
    )

    setGeneratedFinding(null)

    setAnalyzingDiscovery(false)

    setSavingGeneratedFinding(
      false
    )
  }

  // ==================================================
  // ANALYZE DISCOVERY
  // ==================================================

  const analyzeDiscovery =
    async () => {
      setError("")
      setMessage("")

      if (!selectedEngagementId) {
        setError(
          "Please select an engagement first."
        )
        return
      }

      if (!discoveryType.trim()) {
        setError(
          "Tell Notiqx what you discovered first."
        )
        return
      }

      if (!discoveryUrl.trim()) {
        setError(
          "Please provide the affected URL or endpoint."
        )
        return
      }

      if (
        !discoveryNotes.trim() &&
        !discoveryEvidence.trim()
      ) {
        setError(
          "Please provide notes or evidence about the discovery."
        )
        return
      }

      if (
        !discoveryEvidence.trim()
      ) {
        setError(
          "Please provide the evidence or raw output."
        )
        return
      }

      const token =
        localStorage.getItem(
          "access_token"
        )

      if (!token) {
        setIsLoggedIn(false)
        return
      }

      setAnalyzingDiscovery(
        true
      )

      try {
        // ==================================================
        // 1. CREATE DISCOVERY
        // ==================================================

        const rawInput =
          [
            discoveryNotes.trim()
              ? `Notes:\n${discoveryNotes.trim()}`
              : "",

            discoveryEvidence.trim()
              ? `Evidence / Raw Output:\n${discoveryEvidence.trim()}`
              : "",
          ]
            .filter(Boolean)
            .join("\n\n")

        const createResponse =
          await fetch(
            `${API_URL}/engagements/${selectedEngagementId}/discoveries`,
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",

                Authorization:
                  `Bearer ${token}`,
              },

              body: JSON.stringify({
                source:
                  "manual",

                discovery_type:
                  discoveryType.trim(),

                target_url:
                  discoveryUrl.trim(),

                parameter:
                  discoveryParameter.trim() ||
                  null,

                evidence_type:
                  discoveryEvidenceType,

                raw_input:
                  rawInput,
              }),
            }
          )

        const createData =
          await createResponse.json()

        if (!createResponse.ok) {
          if (
            createResponse.status === 401
          ) {
            localStorage.removeItem(
              "access_token"
            )

            setIsLoggedIn(false)

            throw new Error(
              "Your session has expired. Please login again."
            )
          }

          throw new Error(
            createData.detail ||
              "Failed to create discovery."
          )
        }

        const newDiscovery =
          createData.discovery

        if (!newDiscovery?.id) {
          throw new Error(
            "Discovery was created but no discovery ID was returned."
          )
        }

        setDiscoveryId(
          newDiscovery.id
        )

        // ==================================================
        // 2. ANALYZE DISCOVERY
        // ==================================================

        const analyzeResponse =
          await fetch(
            `${API_URL}/discoveries/${newDiscovery.id}/analyze`,
            {
              method: "POST",

              headers: {
                Authorization:
                  `Bearer ${token}`,
              },
            }
          )

        const analyzeData =
          await analyzeResponse.json()

        if (!analyzeResponse.ok) {
          if (
            analyzeResponse.status === 401
          ) {
            localStorage.removeItem(
              "access_token"
            )

            setIsLoggedIn(false)

            throw new Error(
              "Your session has expired. Please login again."
            )
          }

          throw new Error(
            analyzeData.detail ||
              "Failed to analyze discovery."
          )
        }

        const discovery =
          analyzeData.discovery ||
          newDiscovery

        const analysis =
          analyzeData.analysis ||
          {}

        // ==================================================
        // 3. BUILD REVIEW DATA
        // ==================================================

        const generated = {
          title:
            discovery.generated_title ||
            analysis.title ||
            discoveryType.trim(),

          severity:
            discovery.generated_severity ||
            analysis.severity ||
            "informational",

          status:
            "open",

          vulnerability_type:
            discovery.discovery_type ||
            discoveryType.trim(),

          affected_url:
            discovery.target_url ||
            discoveryUrl.trim(),

          affected_parameter:
            discovery.parameter ||
            discoveryParameter.trim() ||
            null,

          cvss_score:
            discovery.generated_cvss ??
            analysis.cvss_score ??
            null,

          cwe_id:
            discovery.generated_cwe ||
            analysis.cwe_id ||
            null,

          description:
            discovery.generated_description ||
            analysis.description ||
            "",

          impact:
            discovery.generated_impact ||
            analysis.impact ||
            "",

          steps_to_reproduce:
            discovery.generated_reproduction ||
            analysis.reproduction ||
            discoveryNotes.trim() ||
            "",

          recommendation:
            discovery.generated_recommendation ||
            analysis.recommendation ||
            "",
        }

        setGeneratedFinding(
          generated
        )

        setMessage(
          "Discovery analyzed successfully. Review the generated finding."
        )

      } catch (err) {
        console.error(
          "Failed to analyze discovery:",
          err
        )

        setError(
          err.message ||
            "Failed to analyze discovery."
        )

      } finally {
        setAnalyzingDiscovery(
          false
        )
      }
    }

  // ==================================================
  // APPROVE DISCOVERY
  // ==================================================

  const saveGeneratedFinding =
    async () => {
      if (!generatedFinding) {
        setError(
          "No generated finding is available."
        )
        return
      }

      if (!discoveryId) {
        setError(
          "No discovery is available to approve."
        )
        return
      }

      if (!selectedEngagementId) {
        setError(
          "No engagement is selected."
        )
        return
      }

      const token =
        localStorage.getItem(
          "access_token"
        )

      if (!token) {
        setIsLoggedIn(false)
        return
      }

      setSavingGeneratedFinding(
        true
      )

      setError("")
      setMessage("")

      try {
        const response =
          await fetch(
            `${API_URL}/discoveries/${discoveryId}/approve`,
            {
              method: "POST",

              headers: {
                Authorization:
                  `Bearer ${token}`,
              },
            }
          )

        const data =
          await response.json()

        if (!response.ok) {
          if (
            response.status === 401
          ) {
            localStorage.removeItem(
              "access_token"
            )

            setIsLoggedIn(false)

            throw new Error(
              "Your session has expired. Please login again."
            )
          }

          throw new Error(
            data.detail ||
              "Failed to approve discovery."
          )
        }

        if (!data.finding) {
          throw new Error(
            "The server did not return the created finding."
          )
        }

        setMessage(
          "Discovery approved, finding created, and evidence attached successfully."
        )

        resetDiscovery()

        setShowDiscovery(false)

        await Promise.all([
          loadEngagementWorkspace(
            selectedEngagementId
          ),

          loadDashboard(),
        ])

      } catch (err) {
        console.error(
          "Failed to approve discovery:",
          err
        )

        setError(
          err.message ||
            "Failed to approve discovery."
        )

      } finally {
        setSavingGeneratedFinding(
          false
        )
      }
    }

  // ==================================================
  // USE EFFECT
  // ==================================================

  useEffect(() => {
    if (isLoggedIn) {
      loadDashboard()
      loadEngagements()
    }
  }, [isLoggedIn])

  // ==================================================
  // LOGOUT
  // ==================================================

  const handleLogout = () => {
    localStorage.removeItem(
      "access_token"
    )

    setIsLoggedIn(false)

    setFullName("")
    setEmail("")
    setPassword("")

    setStats({
      engagements: 0,
      findings: 0,
      evidence: 0,
    })

    setEngagements([])

    setSelectedEngagementId(
      null
    )

    setSelectedEngagement(null)

    setSelectedFindings([])

    resetDiscovery()

    setShowDiscovery(false)

    setShowCreateEngagement(
      false
    )

    setDashboardError("")
    setEngagementsError("")
    setEngagementWorkspaceError("")

    setError("")
    setMessage("")
  }

  // ==================================================
  // SWITCH LOGIN / REGISTER
  // ==================================================

  const switchMode = () => {
    setIsRegister(
      !isRegister
    )

    setFullName("")
    setEmail("")
    setPassword("")

    setError("")
    setMessage("")
  }

  // ==================================================
  // BACK TO DASHBOARD
  // ==================================================

  const backToDashboard = () => {
    setSelectedEngagementId(
      null
    )

    setSelectedEngagement(
      null
    )

    setSelectedFindings([])

    resetDiscovery()

    setShowDiscovery(false)

    setEngagementWorkspaceError("")

    setError("")
    setMessage("")
  }

  // ==================================================
  // UI HELPERS
  // ==================================================

  const getSeverityClasses =
    (severity) => {
      switch (severity) {
        case "critical":
          return "bg-red-950 text-red-400 border-red-800"

        case "high":
          return "bg-orange-950 text-orange-400 border-orange-800"

        case "medium":
          return "bg-yellow-950 text-yellow-400 border-yellow-800"

        case "low":
          return "bg-blue-950 text-blue-400 border-blue-800"

        default:
          return "bg-gray-800 text-gray-400 border-gray-700"
      }
    }

  const getStatusClasses =
    (status) => {
      switch (status) {
        case "open":
          return "bg-red-950 text-red-400 border-red-800"

        case "retesting":
          return "bg-yellow-950 text-yellow-400 border-yellow-800"

        case "remediated":
          return "bg-green-950 text-green-400 border-green-800"

        default:
          return "bg-gray-800 text-gray-400 border-gray-700"
      }
    }

  // ==================================================
  // PROTECTED APP
  // ==================================================

  if (isLoggedIn) {

    // ==================================================
    // ENGAGEMENT WORKSPACE
    // ==================================================

    if (selectedEngagementId) {

      return (
        <div className="min-h-screen bg-gray-950 text-white">

          {/* HEADER */}

          <header className="border-b border-gray-800">

            <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">

              <div>

                <h1 className="text-2xl font-bold">
                  Notiqx
                </h1>

                <p className="text-sm text-gray-500">
                  Automated Pentest Documentation
                </p>

              </div>

              <button
                onClick={
                  handleLogout
                }
                className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm hover:bg-gray-700 transition"
              >
                Logout
              </button>

            </div>

          </header>

          {/* MAIN */}

          <main className="max-w-7xl mx-auto px-6 py-8">

            <button
              onClick={
                backToDashboard
              }
              className="text-sm text-gray-400 hover:text-white transition mb-6"
            >
              ← Back to Dashboard
            </button>

            {engagementWorkspaceLoading && (

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">

                <p className="text-gray-400">
                  Loading engagement...
                </p>

              </div>

            )}

            {engagementWorkspaceError && (

              <div className="bg-red-950 border border-red-800 rounded-xl p-5 text-red-300">
                {engagementWorkspaceError}
              </div>

            )}

            {!engagementWorkspaceLoading &&
              !engagementWorkspaceError &&
              selectedEngagement && (

                <>

                  {/* ENGAGEMENT HEADER */}

                  <div className="bg-gray-900 border border-gray-800 rounded-2xl p-7">

                    <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-5">

                      <div>

                        <p className="text-sm text-gray-500 mb-2">
                          Engagement
                        </p>

                        <h2 className="text-3xl font-bold">
                          {selectedEngagement.name}
                        </h2>

                        <p className="text-gray-400 mt-2">
                          {selectedEngagement.client_name}
                        </p>

                      </div>

                      <span
                        className={
                          selectedEngagement.status ===
                          "active"
                            ? "self-start px-3 py-1.5 rounded-full text-sm bg-green-950 text-green-400 border border-green-800"
                            : "self-start px-3 py-1.5 rounded-full text-sm bg-gray-800 text-gray-400 border border-gray-700"
                        }
                      >
                        {selectedEngagement.status
                          ?.replace(
                            /^\w/,
                            (char) =>
                              char.toUpperCase()
                          )}
                      </span>

                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">

                      <div className="bg-gray-950 border border-gray-800 rounded-xl p-5">

                        <p className="text-xs uppercase tracking-wide text-gray-500">
                          Start Date
                        </p>

                        <p className="text-white font-medium mt-2">
                          {selectedEngagement.start_date ||
                            "—"}
                        </p>

                      </div>

                      <div className="bg-gray-950 border border-gray-800 rounded-xl p-5">

                        <p className="text-xs uppercase tracking-wide text-gray-500">
                          End Date
                        </p>

                        <p className="text-white font-medium mt-2">
                          {selectedEngagement.end_date ||
                            "—"}
                        </p>

                      </div>

                      <div className="bg-gray-950 border border-gray-800 rounded-xl p-5">

                        <p className="text-xs uppercase tracking-wide text-gray-500">
                          Findings
                        </p>

                        <p className="text-2xl font-bold mt-1">
                          {selectedFindings.length}
                        </p>

                      </div>

                    </div>

                    <div className="mt-6">

                      <p className="text-xs uppercase tracking-wide text-gray-500 mb-2">
                        Scope
                      </p>

                      <div className="bg-gray-950 border border-gray-800 rounded-xl p-5">

                        <p className="text-gray-300 whitespace-pre-wrap">
                          {selectedEngagement.scope ||
                            "No scope information provided."}
                        </p>

                      </div>

                    </div>

                  </div>

                  {/* FINDINGS */}

                  <div className="mt-8">

                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-5">

                      <div>

                        <h3 className="text-2xl font-bold">
                          Findings
                        </h3>

                        <p className="text-gray-400 text-sm mt-1">
                          Document vulnerabilities with minimal manual work.
                        </p>

                      </div>

                      <button
                        onClick={() => {

                          const next =
                            !showDiscovery

                          setShowDiscovery(
                            next
                          )

                          if (!next) {
                            resetDiscovery()
                          }

                          setError("")
                          setMessage("")

                        }}
                        className="px-5 py-3 bg-white text-gray-950 font-semibold rounded-lg hover:bg-gray-200 transition"
                      >
                        {showDiscovery
                          ? "Close Discovery"
                          : "+ New Discovery"}
                      </button>

                    </div>

                    {/* DISCOVERY */}

                    {showDiscovery && (

                      <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 mb-7">

                        {!generatedFinding ? (

                          <>

                            <div className="mb-7">

                              <div className="flex items-center gap-3">

                                <div className="w-10 h-10 rounded-lg bg-gray-800 flex items-center justify-center">
                                  🔎
                                </div>

                                <div>

                                  <h4 className="text-xl font-semibold">
                                    New Discovery
                                  </h4>

                                  <p className="text-gray-500 text-sm">
                                    Give Notiqx the important information. We'll handle the documentation.
                                  </p>

                                </div>

                              </div>

                            </div>

                            {/* DISCOVERY TYPE */}

                            <div className="mb-5">

                              <label className="block text-sm text-gray-300 mb-2">
                                What did you discover?
                              </label>

                              <select
                                value={
                                  discoveryType
                                }
                                onChange={(
                                  event
                                ) =>
                                  setDiscoveryType(
                                    event.target.value
                                  )
                                }
                                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white outline-none focus:border-gray-500"
                              >

                                <option value="">
                                  Select discovery type
                                </option>

                                <option value="SQL Injection">
                                  SQL Injection
                                </option>

                                <option value="Cross-Site Scripting (XSS)">
                                  Cross-Site Scripting (XSS)
                                </option>

                                <option value="IDOR / Broken Access Control">
                                  IDOR / Broken Access Control
                                </option>

                                <option value="SSRF">
                                  SSRF
                                </option>

                                <option value="Information Disclosure">
                                  Information Disclosure
                                </option>

                                <option value="Missing Security Headers">
                                  Missing Security Headers
                                </option>

                                <option value="Other">
                                  Other
                                </option>

                              </select>

                            </div>

                            {/* URL + PARAMETER */}

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">

                              <div>

                                <label className="block text-sm text-gray-300 mb-2">
                                  Affected URL / Endpoint
                                </label>

                                <input
                                  type="text"
                                  value={
                                    discoveryUrl
                                  }
                                  onChange={(
                                    event
                                  ) =>
                                    setDiscoveryUrl(
                                      event.target.value
                                    )
                                  }
                                  placeholder="https://target.com/login"
                                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 outline-none focus:border-gray-500"
                                />

                              </div>

                              <div>

                                <label className="block text-sm text-gray-300 mb-2">
                                  Parameter
                                </label>

                                <input
                                  type="text"
                                  value={
                                    discoveryParameter
                                  }
                                  onChange={(
                                    event
                                  ) =>
                                    setDiscoveryParameter(
                                      event.target.value
                                    )
                                  }
                                  placeholder="username"
                                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 outline-none focus:border-gray-500"
                                />

                              </div>

                            </div>

                            {/* NOTES */}

                            <div className="mt-5">

                              <label className="block text-sm text-gray-300 mb-2">
                                What happened?
                              </label>

                              <textarea
                                value={
                                  discoveryNotes
                                }
                                onChange={(
                                  event
                                ) =>
                                  setDiscoveryNotes(
                                    event.target.value
                                  )
                                }
                                placeholder="I changed the username parameter and was able to manipulate the SQL query..."
                                rows="5"
                                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 outline-none focus:border-gray-500 resize-y"
                              />

                              <p className="text-xs text-gray-600 mt-2">
                                Write it in your own words. It doesn't have to be professional.
                              </p>

                            </div>

                            {/* EVIDENCE TYPE */}

                            <div className="mt-5">

                              <label className="block text-sm text-gray-300 mb-2">
                                Evidence Type
                              </label>

                              <select
                                value={
                                  discoveryEvidenceType
                                }
                                onChange={(
                                  event
                                ) =>
                                  setDiscoveryEvidenceType(
                                    event.target.value
                                  )
                                }
                                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white outline-none focus:border-gray-500"
                              >

                                <option value="http_request">
                                  HTTP Request
                                </option>

                                <option value="tool_output">
                                  Tool Output
                                </option>

                                <option value="note">
                                  Pentester Note
                                </option>

                                <option value="curl_command">
                                  cURL Command
                                </option>

                                <option value="code_snippet">
                                  Code Snippet
                                </option>

                              </select>

                              <p className="text-xs text-gray-600 mt-2">
                                Choose what kind of evidence you are providing.
                              </p>

                            </div>

                            {/* EVIDENCE */}

                            <div className="mt-5">

                              <label className="block text-sm text-gray-300 mb-2">
                                Evidence / Raw Output
                              </label>

                              <textarea
                                value={
                                  discoveryEvidence
                                }
                                onChange={(
                                  event
                                ) =>
                                  setDiscoveryEvidence(
                                    event.target.value
                                  )
                                }
                                placeholder={
                                  discoveryEvidenceType ===
                                  "http_request"
                                    ? "GET /search?id=1' HTTP/1.1\nHost: target.com"
                                    : discoveryEvidenceType ===
                                      "curl_command"
                                      ? "curl -i 'https://target.com/search?id=1'"
                                      : discoveryEvidenceType ===
                                        "code_snippet"
                                        ? "Paste the relevant code here..."
                                        : discoveryEvidenceType ===
                                          "tool_output"
                                          ? "Paste Nmap, Nuclei, Burp, or other tool output..."
                                          : "Write the supporting pentester note..."
                                }
                                rows="8"
                                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 outline-none focus:border-gray-500 resize-y font-mono text-sm"
                              />

                              <p className="text-xs text-gray-600 mt-2">
                                This evidence will automatically be attached to the finding after approval.
                              </p>

                            </div>

                            {/* ACTION */}

                            <div className="mt-7 flex justify-end">

                              <button
                                onClick={
                                  analyzeDiscovery
                                }
                                disabled={
                                  analyzingDiscovery
                                }
                                className="px-6 py-3 bg-white text-gray-950 font-semibold rounded-lg hover:bg-gray-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
                              >

                                {analyzingDiscovery
                                  ? "Analyzing..."
                                  : "Analyze Discovery →"}

                              </button>

                            </div>

                          </>

                        ) : (

                          <>

                            {/* GENERATED FINDING */}

                            <div className="mb-7">

                              <div className="flex items-center gap-3">

                                <div className="w-10 h-10 rounded-lg bg-green-950 border border-green-800 flex items-center justify-center">
                                  ✓
                                </div>

                                <div>

                                  <h4 className="text-xl font-semibold">
                                    Finding Generated
                                  </h4>

                                  <p className="text-gray-500 text-sm">
                                    Review Notiqx's generated documentation before approving it.
                                  </p>

                                </div>

                              </div>

                            </div>

                            {/* REVIEW WARNING */}

                            <div className="mb-6 p-4 rounded-lg bg-yellow-950 border border-yellow-800 text-yellow-300 text-sm">

                              <strong>
                                Human Review Required:
                              </strong>

                              {" "}
                              Review the generated documentation before approving this finding.

                            </div>

                            {/* TITLE */}

                            <div>

                              <label className="block text-sm text-gray-300 mb-2">
                                Title
                              </label>

                              <input
                                type="text"
                                value={
                                  generatedFinding.title
                                }
                                onChange={(
                                  event
                                ) =>
                                  setGeneratedFinding({
                                    ...generatedFinding,

                                    title:
                                      event.target.value,
                                  })
                                }
                                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white outline-none"
                              />

                            </div>

                            {/* SEVERITY / CWE / CVSS */}

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-5">

                              <div>

                                <label className="block text-sm text-gray-300 mb-2">
                                  Severity
                                </label>

                                <select
                                  value={
                                    generatedFinding.severity
                                  }
                                  onChange={(
                                    event
                                  ) =>
                                    setGeneratedFinding({
                                      ...generatedFinding,

                                      severity:
                                        event.target.value,
                                    })
                                  }
                                  className={`w-full px-4 py-3 rounded-lg border outline-none ${getSeverityClasses(
                                    generatedFinding.severity
                                  )}`}
                                >

                                  <option value="critical">
                                    Critical
                                  </option>

                                  <option value="high">
                                    High
                                  </option>

                                  <option value="medium">
                                    Medium
                                  </option>

                                  <option value="low">
                                    Low
                                  </option>

                                  <option value="informational">
                                    Informational
                                  </option>

                                </select>

                              </div>

                              <div>

                                <label className="block text-sm text-gray-300 mb-2">
                                  CWE
                                </label>

                                <input
                                  type="text"
                                  value={
                                    generatedFinding.cwe_id ||
                                    ""
                                  }
                                  onChange={(
                                    event
                                  ) =>
                                    setGeneratedFinding({
                                      ...generatedFinding,

                                      cwe_id:
                                        event.target.value ||
                                        null,
                                    })
                                  }
                                  placeholder="CWE-89"
                                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white outline-none"
                                />

                              </div>

                              <div>

                                <label className="block text-sm text-gray-300 mb-2">
                                  CVSS
                                </label>

                                <input
                                  type="number"
                                  min="0"
                                  max="10"
                                  step="0.1"
                                  value={
                                    generatedFinding.cvss_score ??
                                    ""
                                  }
                                  onChange={(
                                    event
                                  ) =>
                                    setGeneratedFinding({
                                      ...generatedFinding,

                                      cvss_score:
                                        event.target.value ===
                                        ""
                                          ? null
                                          : Number(
                                              event.target.value
                                            ),
                                    })
                                  }
                                  placeholder="8.8"
                                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white outline-none"
                                />

                              </div>

                            </div>

                            {/* URL */}

                            <div className="mt-5">

                              <label className="block text-sm text-gray-300 mb-2">
                                Affected URL / Endpoint
                              </label>

                              <input
                                type="text"
                                value={
                                  generatedFinding.affected_url ||
                                  ""
                                }
                                onChange={(
                                  event
                                ) =>
                                  setGeneratedFinding({
                                    ...generatedFinding,

                                    affected_url:
                                      event.target.value,
                                  })
                                }
                                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white outline-none"
                              />

                            </div>

                            {/* PARAMETER */}

                            <div className="mt-5">

                              <label className="block text-sm text-gray-300 mb-2">
                                Affected Parameter
                              </label>

                              <input
                                type="text"
                                value={
                                  generatedFinding.affected_parameter ||
                                  ""
                                }
                                onChange={(
                                  event
                                ) =>
                                  setGeneratedFinding({
                                    ...generatedFinding,

                                    affected_parameter:
                                      event.target.value ||
                                      null,
                                  })
                                }
                                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white outline-none"
                              />

                            </div>

                            {/* DESCRIPTION */}

                            <div className="mt-5">

                              <label className="block text-sm text-gray-300 mb-2">
                                Description
                              </label>

                              <textarea
                                value={
                                  generatedFinding.description ||
                                  ""
                                }
                                onChange={(
                                  event
                                ) =>
                                  setGeneratedFinding({
                                    ...generatedFinding,

                                    description:
                                      event.target.value,
                                  })
                                }
                                rows="6"
                                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white outline-none resize-y"
                              />

                            </div>

                            {/* IMPACT */}

                            <div className="mt-5">

                              <label className="block text-sm text-gray-300 mb-2">
                                Impact
                              </label>

                              <textarea
                                value={
                                  generatedFinding.impact ||
                                  ""
                                }
                                onChange={(
                                  event
                                ) =>
                                  setGeneratedFinding({
                                    ...generatedFinding,

                                    impact:
                                      event.target.value,
                                  })
                                }
                                rows="6"
                                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white outline-none resize-y"
                              />

                            </div>

                            {/* STEPS */}

                            <div className="mt-5">

                              <label className="block text-sm text-gray-300 mb-2">
                                Steps to Reproduce
                              </label>

                              <textarea
                                value={
                                  generatedFinding.steps_to_reproduce ||
                                  ""
                                }
                                onChange={(
                                  event
                                ) =>
                                  setGeneratedFinding({
                                    ...generatedFinding,

                                    steps_to_reproduce:
                                      event.target.value,
                                  })
                                }
                                rows="7"
                                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white outline-none resize-y"
                              />

                            </div>

                            {/* RECOMMENDATION */}

                            <div className="mt-5">

                              <label className="block text-sm text-gray-300 mb-2">
                                Recommendation
                              </label>

                              <textarea
                                value={
                                  generatedFinding.recommendation ||
                                  ""
                                }
                                onChange={(
                                  event
                                ) =>
                                  setGeneratedFinding({
                                    ...generatedFinding,

                                    recommendation:
                                      event.target.value,
                                  })
                                }
                                rows="6"
                                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white outline-none resize-y"
                              />

                            </div>

                            {/* EVIDENCE PREVIEW */}

                            <div className="mt-6">

                              <label className="block text-sm text-gray-300 mb-2">
                                Evidence to Attach
                              </label>

                              <div className="bg-gray-950 border border-gray-800 rounded-xl p-5">

                                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">

                                  <div>

                                    <p className="text-white font-medium">
                                      {discoveryEvidenceType ===
                                      "http_request"
                                        ? "HTTP Request"
                                        : discoveryEvidenceType ===
                                          "tool_output"
                                          ? "Tool Output"
                                          : discoveryEvidenceType ===
                                            "curl_command"
                                            ? "cURL Command"
                                            : discoveryEvidenceType ===
                                              "code_snippet"
                                              ? "Code Snippet"
                                              : "Pentester Note"}
                                    </p>

                                    <p className="text-xs text-gray-500 mt-1">
                                      Automatically attached when approved
                                    </p>

                                  </div>

                                  <span className="px-2.5 py-1 rounded-full text-xs bg-gray-800 text-gray-400 border border-gray-700">
                                    Evidence
                                  </span>

                                </div>

                                <pre className="text-sm text-gray-400 whitespace-pre-wrap break-words font-mono overflow-x-auto">
                                  {discoveryEvidence ||
                                    "No evidence provided."}
                                </pre>

                              </div>

                            </div>

                            {/* ACTIONS */}

                            <div className="mt-7 flex flex-col md:flex-row md:items-center md:justify-between gap-3">

                              <button
                                onClick={() => {

                                  setGeneratedFinding(
                                    null
                                  )

                                  setError("")
                                  setMessage("")

                                }}
                                disabled={
                                  savingGeneratedFinding
                                }
                                className="px-5 py-3 bg-gray-800 border border-gray-700 text-white font-semibold rounded-lg hover:bg-gray-700 transition disabled:opacity-50"
                              >
                                ← Edit Discovery
                              </button>

                              <button
                                onClick={
                                  saveGeneratedFinding
                                }
                                disabled={
                                  savingGeneratedFinding
                                }
                                className="px-6 py-3 bg-white text-gray-950 font-semibold rounded-lg hover:bg-gray-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
                              >

                                {savingGeneratedFinding
                                  ? "Approving..."
                                  : "✓ Approve & Save Finding"}

                              </button>

                            </div>

                          </>

                        )}

                      </div>

                    )}

                    {/* MESSAGES */}

                    {message && (

                      <div className="mb-5 p-4 rounded-lg bg-green-950 border border-green-800 text-green-300 text-sm">
                        {message}
                      </div>

                    )}

                    {error && (

                      <div className="mb-5 p-4 rounded-lg bg-red-950 border border-red-800 text-red-300 text-sm">
                        {error}
                      </div>

                    )}

                    {/* FINDING LIST */}

                    {selectedFindings.length ===
                    0 ? (

                      <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">

                        <div className="text-4xl mb-4">
                          🔎
                        </div>

                        <h4 className="text-lg font-semibold">
                          No findings yet
                        </h4>

                        <p className="text-gray-500 text-sm mt-2">
                          Discover a vulnerability and let Notiqx handle the documentation.
                        </p>

                        {!showDiscovery && (

                          <button
                            onClick={() => {

                              setShowDiscovery(
                                true
                              )

                              setError("")
                              setMessage("")

                            }}
                            className="mt-5 px-5 py-2.5 bg-white text-gray-950 font-semibold rounded-lg hover:bg-gray-200 transition"
                          >
                            Start New Discovery
                          </button>

                        )}

                      </div>

                    ) : (

                      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">

                        <div className="hidden md:grid grid-cols-12 gap-4 px-6 py-4 border-b border-gray-800 text-xs uppercase tracking-wide text-gray-500">

                          <div className="col-span-5">
                            Finding
                          </div>

                          <div className="col-span-2">
                            Severity
                          </div>

                          <div className="col-span-2">
                            Status
                          </div>

                          <div className="col-span-3">
                            Type
                          </div>

                        </div>

                        {selectedFindings.map(
                          (finding) => (

                            <div
                              key={
                                finding.id
                              }
                              className="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4 px-6 py-5 border-b border-gray-800 last:border-b-0 hover:bg-gray-800/40 transition"
                            >

                              <div className="md:col-span-5">

                                <p className="font-semibold text-white">
                                  {finding.title}
                                </p>

                                {finding.affected_url && (

                                  <p className="text-xs text-gray-500 mt-2 truncate">
                                    {finding.affected_url}
                                  </p>

                                )}

                              </div>

                              <div className="md:col-span-2 flex items-center">

                                <span
                                  className={`px-2.5 py-1 rounded-full text-xs border ${getSeverityClasses(
                                    finding.severity
                                  )}`}
                                >
                                  {finding.severity
                                    ?.replace(
                                      /^\w/,
                                      (char) =>
                                        char.toUpperCase()
                                    )}
                                </span>

                              </div>

                              <div className="md:col-span-2 flex items-center">

                                <span
                                  className={`px-2.5 py-1 rounded-full text-xs border ${getStatusClasses(
                                    finding.status
                                  )}`}
                                >
                                  {finding.status
                                    ?.replace(
                                      /^\w/,
                                      (char) =>
                                        char.toUpperCase()
                                    )}
                                </span>

                              </div>

                              <div className="md:col-span-3 flex items-center">

                                <p className="text-sm text-gray-400">
                                  {finding.vulnerability_type ||
                                    "—"}
                                </p>

                              </div>

                            </div>

                          )
                        )}

                      </div>

                    )}

                  </div>

                  {/* OTHER MODULES */}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">

                    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">

                      <p className="text-xs uppercase tracking-wide text-gray-500">
                        Evidence
                      </p>

                      <h4 className="text-xl font-semibold mt-2">
                        Evidence Automation
                      </h4>

                      <p className="text-gray-500 text-sm mt-2">
                        HTTP requests, tool output, notes, cURL commands and code snippets can now be classified automatically.
                      </p>

                    </div>

                    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">

                      <p className="text-xs uppercase tracking-wide text-gray-500">
                        Reports
                      </p>

                      <h4 className="text-xl font-semibold mt-2">
                        Automated Reporting
                      </h4>

                      <p className="text-gray-500 text-sm mt-2">
                        Approved findings and their evidence will flow into the final pentest report.
                      </p>

                    </div>

                  </div>

                </>

              )}

          </main>

        </div>
      )
    }

    // ==================================================
    // DASHBOARD
    // ==================================================

    return (
      <div className="min-h-screen bg-gray-950 text-white">

        <header className="border-b border-gray-800">

          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">

            <div>

              <h1 className="text-2xl font-bold">
                Notiqx
              </h1>

              <p className="text-sm text-gray-500">
                Automated Pentest Documentation
              </p>

            </div>

            <button
              onClick={
                handleLogout
              }
              className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm hover:bg-gray-700 transition"
            >
              Logout
            </button>

          </div>

        </header>

        <main className="max-w-7xl mx-auto px-6 py-10">

          <div className="flex items-center justify-between">

            <div>

              <h2 className="text-3xl font-bold">
                Dashboard
              </h2>

              <p className="text-gray-400 mt-2">
                Manage your penetration testing engagements.
              </p>

            </div>

            <button
              onClick={() => {

                loadDashboard()
                loadEngagements()

              }}
              disabled={
                dashboardLoading ||
                engagementsLoading
              }
              className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm hover:bg-gray-700 transition disabled:opacity-50"
            >

              {dashboardLoading ||
              engagementsLoading
                ? "Refreshing..."
                : "Refresh"}

            </button>

          </div>

          {message && (

            <div className="mt-6 p-4 rounded-lg bg-green-950 border border-green-800 text-green-300 text-sm">
              {message}
            </div>

          )}

          {error && (

            <div className="mt-6 p-4 rounded-lg bg-red-950 border border-red-800 text-red-300 text-sm">
              {error}
            </div>

          )}

          {dashboardError && (

            <div className="mt-6 p-4 rounded-lg bg-red-950 border border-red-800 text-red-300 text-sm">
              {dashboardError}
            </div>

          )}

          {/* STATS */}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">

              <p className="text-gray-400 text-sm">
                Engagements
              </p>

              <p className="text-3xl font-bold mt-2">
                {dashboardLoading
                  ? "..."
                  : stats.engagements}
              </p>

            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">

              <p className="text-gray-400 text-sm">
                Findings
              </p>

              <p className="text-3xl font-bold mt-2">
                {dashboardLoading
                  ? "..."
                  : stats.findings}
              </p>

            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">

              <p className="text-gray-400 text-sm">
                Evidence
              </p>

              <p className="text-3xl font-bold mt-2">
                {dashboardLoading
                  ? "..."
                  : stats.evidence}
              </p>

            </div>

          </div>

          {/* ENGAGEMENTS */}

          <div className="mt-10">

            <div className="flex items-center justify-between mb-5">

              <div>

                <h3 className="text-2xl font-bold">
                  Engagements
                </h3>

                <p className="text-gray-400 text-sm mt-1">
                  Manage your penetration testing projects.
                </p>

              </div>

              <button
                onClick={() => {

                  setShowCreateEngagement(
                    !showCreateEngagement
                  )

                  setError("")
                  setMessage("")

                }}
                className="px-4 py-2 bg-white text-gray-950 font-semibold rounded-lg hover:bg-gray-200 transition"
              >
                {showCreateEngagement
                  ? "Cancel"
                  : "+ New Engagement"}
              </button>

            </div>

            {/* CREATE ENGAGEMENT */}

            {showCreateEngagement && (

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">

                <h4 className="text-xl font-semibold mb-6">
                  New Engagement
                </h4>

                <form
                  onSubmit={
                    handleCreateEngagement
                  }
                >

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">

                    <div>

                      <label className="block text-sm text-gray-300 mb-2">
                        Engagement Name
                      </label>

                      <input
                        type="text"
                        value={
                          engagementName
                        }
                        onChange={(
                          event
                        ) =>
                          setEngagementName(
                            event.target.value
                          )
                        }
                        placeholder="Web Application Pentest"
                        className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 outline-none focus:border-gray-500"
                      />

                    </div>

                    <div>

                      <label className="block text-sm text-gray-300 mb-2">
                        Client Name
                      </label>

                      <input
                        type="text"
                        value={
                          clientName
                        }
                        onChange={(
                          event
                        ) =>
                          setClientName(
                            event.target.value
                          )
                        }
                        placeholder="Example Corporation"
                        className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 outline-none focus:border-gray-500"
                      />

                    </div>

                    <div>

                      <label className="block text-sm text-gray-300 mb-2">
                        Start Date
                      </label>

                      <input
                        type="date"
                        value={
                          startDate
                        }
                        onChange={(
                          event
                        ) =>
                          setStartDate(
                            event.target.value
                          )
                        }
                        className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white outline-none"
                      />

                    </div>

                    <div>

                      <label className="block text-sm text-gray-300 mb-2">
                        End Date
                      </label>

                      <input
                        type="date"
                        value={
                          endDate
                        }
                        onChange={(
                          event
                        ) =>
                          setEndDate(
                            event.target.value
                          )
                        }
                        className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white outline-none"
                      />

                    </div>

                    <div>

                      <label className="block text-sm text-gray-300 mb-2">
                        Status
                      </label>

                      <select
                        value={
                          engagementStatus
                        }
                        onChange={(
                          event
                        ) =>
                          setEngagementStatus(
                            event.target.value
                          )
                        }
                        className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white outline-none"
                      >

                        <option value="active">
                          Active
                        </option>

                        <option value="completed">
                          Completed
                        </option>

                      </select>

                    </div>

                  </div>

                  <div className="mt-5">

                    <label className="block text-sm text-gray-300 mb-2">
                      Scope
                    </label>

                    <textarea
                      value={
                        scope
                      }
                      onChange={(
                        event
                      ) =>
                        setScope(
                          event.target.value
                        )
                      }
                      placeholder="example.com, api.example.com"
                      rows="4"
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 outline-none resize-none"
                    />

                  </div>

                  <div className="mt-6 flex justify-end">

                    <button
                      type="submit"
                      disabled={
                        creatingEngagement
                      }
                      className="px-6 py-3 bg-white text-gray-950 font-semibold rounded-lg hover:bg-gray-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >

                      {creatingEngagement
                        ? "Creating..."
                        : "Create Engagement"}

                    </button>

                  </div>

                </form>

              </div>

            )}

            {engagementsError && (

              <div className="mb-5 p-4 rounded-lg bg-red-950 border border-red-800 text-red-300 text-sm">
                {engagementsError}
              </div>

            )}

            {/* ENGAGEMENT LIST */}

            {engagementsLoading ? (

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-10 text-center">

                <p className="text-gray-400">
                  Loading engagements...
                </p>

              </div>

            ) : engagements.length ===
              0 ? (

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-10 text-center">

                <h4 className="text-lg font-semibold">
                  No engagements yet
                </h4>

                <p className="text-gray-500 text-sm mt-2">
                  Create your first penetration testing engagement.
                </p>

              </div>

            ) : (

              <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">

                <div className="grid grid-cols-12 gap-4 px-6 py-4 border-b border-gray-800 text-xs uppercase tracking-wide text-gray-500">

                  <div className="col-span-4">
                    Engagement
                  </div>

                  <div className="col-span-3">
                    Client
                  </div>

                  <div className="col-span-2">
                    Status
                  </div>

                  <div className="col-span-3">
                    Dates
                  </div>

                </div>

                {engagements.map(
                  (engagement) => (

                    <div
                      key={
                        engagement.id
                      }
                      onClick={() =>
                        loadEngagementWorkspace(
                          engagement.id
                        )
                      }
                      className="grid grid-cols-12 gap-4 px-6 py-5 border-b border-gray-800 last:border-b-0 hover:bg-gray-800/40 transition cursor-pointer"
                    >

                      <div className="col-span-4">

                        <p className="font-semibold text-white">
                          {engagement.name}
                        </p>

                        {engagement.scope && (

                          <p className="text-xs text-gray-500 mt-1 truncate">
                            {engagement.scope}
                          </p>

                        )}

                      </div>

                      <div className="col-span-3 flex items-center">

                        <p className="text-gray-300">
                          {engagement.client_name}
                        </p>

                      </div>

                      <div className="col-span-2 flex items-center">

                        <span
                          className={
                            engagement.status ===
                            "active"
                              ? "px-2.5 py-1 rounded-full text-xs bg-green-950 text-green-400 border border-green-800"
                              : "px-2.5 py-1 rounded-full text-xs bg-gray-800 text-gray-400 border border-gray-700"
                          }
                        >

                          {engagement.status
                            ?.replace(
                              /^\w/,
                              (char) =>
                                char.toUpperCase()
                            )}

                        </span>

                      </div>

                      <div className="col-span-3 flex items-center">

                        <p className="text-sm text-gray-400">

                          {engagement.start_date ||
                            "—"}

                          {" → "}

                          {engagement.end_date ||
                            "—"}

                        </p>

                      </div>

                    </div>

                  )
                )}

              </div>

            )}

          </div>

        </main>

      </div>
    )
  }

  // ==================================================
  // LOGIN / REGISTER
  // ==================================================

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">

      <div className="w-full max-w-md">

        {/* BRAND */}

        <div className="text-center mb-8">

          <h1 className="text-4xl font-bold text-white">
            Notiqx
          </h1>

          <p className="text-gray-400 mt-2">
            Penetration Testing, Organized.
          </p>

        </div>

        {/* AUTH CARD */}

        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8 shadow-xl">

          <h2 className="text-2xl font-semibold text-white text-center">

            {isRegister
              ? "Create your account"
              : "Welcome back"}

          </h2>

          <p className="text-gray-400 text-sm text-center mt-2 mb-6">

            {isRegister
              ? "Create your Notiqx account"
              : "Sign in to your Notiqx account"}

          </p>

          {error && (

            <div className="mb-4 p-3 rounded-lg bg-red-950 border border-red-800 text-red-300 text-sm">
              {error}
            </div>

          )}

          {message && (

            <div className="mb-4 p-3 rounded-lg bg-green-950 border border-green-800 text-green-300 text-sm">
              {message}
            </div>

          )}

          <form
            onSubmit={
              isRegister
                ? handleRegister
                : handleLogin
            }
          >

            {isRegister && (

              <div className="mb-4">

                <label className="block text-sm text-gray-300 mb-2">
                  Full Name
                </label>

                <input
                  type="text"
                  value={
                    fullName
                  }
                  onChange={(
                    event
                  ) =>
                    setFullName(
                      event.target.value
                    )
                  }
                  placeholder="Your full name"
                  autoComplete="name"
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 outline-none focus:border-gray-500"
                />

              </div>

            )}

            <div className="mb-4">

              <label className="block text-sm text-gray-300 mb-2">
                Email
              </label>

              <input
                type="email"
                value={
                  email
                }
                onChange={(
                  event
                ) =>
                  setEmail(
                    event.target.value
                  )
                }
                placeholder="you@example.com"
                autoComplete="email"
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 outline-none focus:border-gray-500"
              />

            </div>

            <div className="mb-6">

              <label className="block text-sm text-gray-300 mb-2">
                Password
              </label>

              <input
                type="password"
                value={
                  password
                }
                onChange={(
                  event
                ) =>
                  setPassword(
                    event.target.value
                  )
                }
                placeholder="••••••••"
                autoComplete={
                  isRegister
                    ? "new-password"
                    : "current-password"
                }
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 outline-none focus:border-gray-500"
              />

              {isRegister && (

                <p className="text-xs text-gray-500 mt-2">
                  Minimum 8 characters.
                </p>

              )}

            </div>

            <button
              type="submit"
              disabled={
                loading
              }
              className="w-full py-3 bg-white text-gray-950 font-semibold rounded-lg hover:bg-gray-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >

              {loading
                ? isRegister
                  ? "Creating Account..."
                  : "Logging in..."
                : isRegister
                  ? "Create Account"
                  : "Login"}

            </button>

          </form>

          <div className="text-center mt-6">

            <span className="text-sm text-gray-400">

              {isRegister
                ? "Already have an account? "
                : "Don't have an account? "}

            </span>

            <button
              type="button"
              onClick={
                switchMode
              }
              className="text-sm text-white font-semibold hover:underline"
            >

              {isRegister
                ? "Login"
                : "Register"}

            </button>

          </div>

        </div>

      </div>

    </div>
  )
}

export default App