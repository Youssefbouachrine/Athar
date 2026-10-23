
document.addEventListener("DOMContentLoaded", () => {
    const communitySelect = document.getElementById("list-comm");
    const form = document.getElementById("dashboard-filters");
    const results = document.getElementById("filter-results");

    if (!communitySelect || !form || !results) {
        console.error("Missing community select, filters form, or results.");
        return;
    }

    const startDate = document.getElementById("start-date");
    const endDate = document.getElementById("end-date");
    const activityType = document.getElementById("activity-type");
    const projectStatus = document.getElementById("project-status");
    const resetButton = document.getElementById("reset-filters");

    let allProjects = [];
    let filteredMode = false;
    let requestId = 0;

    
function displayProjects(projects) {
    results.replaceChildren();

    if (projects.length === 0) {
        results.textContent = "No projects found.";
        return;
    }

    const grid = document.createElement("div");
    grid.className = "projects-grid";

    projects.forEach(project => {
        const card = document.createElement("div");
        card.className = "project-card";

        const title = document.createElement("h3");
        title.textContent =
            project.title || project.name || project.project || "Untitled project";

        const status = document.createElement("p");
        status.className = "project-status";
        status.textContent = `Status: ${project.status || "Unknown"}`;

        const community = document.createElement("p");
        community.className = "project-community";
        community.textContent =
            `Community: ${
                project.community_name ||
                project.community ||
                communitySelect.selectedOptions[0]?.textContent ||
                "Unknown"
            }`;
        const project_type = document.createElement("p");
        project_type.className = "project-type";
        project_type.textContent = project.project_type

        card.append(title, status, community, project_type);
        grid.appendChild(card);
    });

    results.appendChild(grid);

    document.dispatchEvent(
        new CustomEvent("dashboard:filtered", {
            detail: { projects }
        })
    );
}


    async function loadCommunities() {
        const response = await fetch("/api/communities");

        if (!response.ok) {
            throw new Error(`Communities API: HTTP ${response.status}`);
        }

        const data = await response.json();
        const communities = Array.isArray(data)
            ? data
            : data.communities;

        if (!Array.isArray(communities)) {
            throw new Error("Invalid communities response");
        }

        communitySelect.replaceChildren(
            new Option("Choose a community", "")
        );

        communities.forEach(community => {
            communitySelect.add(
                new Option(community.name, community.slug)
            );
        });
    }

    async function loadProjects() {
        const slug = communitySelect.value;
        const currentRequest = ++requestId;

        allProjects = [];
        filteredMode = false;
        displayProjects([]);

        if (!slug) {
            results.textContent = "Choose a community to display its projects.";
            return;
        }

        results.textContent = "Loading projects...";

        try {
            const response = await fetch(
                `/api/${slug}/projects`
            );

            if (!response.ok) {
                throw new Error(`Projects API: HTTP ${response.status}`);
            }

            const data = await response.json();

            if (currentRequest !== requestId) return;

            allProjects = Array.isArray(data)
                ? data
                : data.projects;

            if (!Array.isArray(allProjects)) {
                throw new Error("Invalid projects response");
            }

            // Initial display: ALL projects, no filters applied.
            displayProjects(allProjects);
        } catch (error) {
            if (currentRequest === requestId) {
                console.error(error);
                results.textContent = `Error: ${error.message}`;
            }
        }
    }

    

function normalize(value) {
    return String(value ?? "")
        .toLowerCase()
        .trim()
        .replace(/[-_]+/g, " ")
        .replace(/\s+/g, " ")
        .replace(/s$/, "");
}

function applyFilters() {
    const start = startDate?.value || "";
    const end = endDate?.value || "";
    const selectedType = activityType?.value || "";
    const selectedStatus = projectStatus?.value || "";

    const filteredProjects = allProjects.filter(project => {
        const projectDate = String(
            project.date ??
            project.start_date ??
            project.startDate ??
            ""
        ).slice(0, 10);

        const projectType =
            project.type ??
            project.activity_type ??
            project.project_type ??
            project.activityType ??
            "";

        const projectState =
            project.status ??
            project.project_status ??
            "";

        if (start && (!projectDate || projectDate < start)) {
            return false;
        }

        if (end && (!projectDate || projectDate > end)) {
            return false;
        }

        if (
            selectedType &&
            normalize(projectType) !== normalize(selectedType)
        ) {
            return false;
        }

        if (
            selectedStatus &&
            normalize(projectState) !== normalize(selectedStatus)
        ) {
            return false;
        }

        return true;
    });

    console.log("Selected type:", selectedType);
    console.log("Projects before filter:", allProjects.length);
    console.log("Projects after filter:", filteredProjects.length);

    displayProjects(filteredProjects);
}



    form.addEventListener("submit", event => {
        event.preventDefault();
        applyFilters();
    });

    if (resetButton) {
        resetButton.addEventListener("click", () => {
            form.reset();
            filteredMode = false;
            displayProjects(allProjects);
        });
    }

    communitySelect.addEventListener("change", loadProjects);

    loadCommunities()
        .then(() => {
            // If a community is preselected, load its projects.
            if (communitySelect.value) {
                loadProjects();
            } else {
                results.textContent = "Choose a community to display its projects.";
            }
        })
        .catch(error => {
            console.error(error);
            results.textContent = "Could not load communities.";
        });
});
