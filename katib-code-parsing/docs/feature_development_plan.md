# Feature Development Plan: Code Comparison and Enhanced Editor

## 1. Overview

This document outlines the development plan for two new major features:
1.  **Code Version Comparison (Diff):** A feature to visually compare two different versions of a code.
2.  **Enhanced Code Editor:** Replacing the standard `<textarea>` with a modern code editor that supports syntax highlighting.

These features will significantly improve user experience, making code management and editing more efficient and intuitive.

---

## 2. Feature 1: Code Version Comparison (Diff)

### Objective

To allow users to select any two versions of a code and see a clear, side-by-side comparison highlighting the differences. This helps in tracking changes, understanding the impact of modifications, and debugging.

### Proposed Library

-   **`react-diff-viewer-continued`**: A well-maintained and flexible React component for displaying text diffs. It supports side-by-side and inline views, syntax highlighting, and is easy to integrate.

### UI/UX Design

1.  **Entry Point:** A "Compare Versions" button will be added to the `CodeDetail.tsx` component, likely near the version selection dropdown.
2.  **Comparison Modal:**
    -   Clicking the button will open a modal window.
    -   The modal will contain two dropdown menus, labeled "Old Version" and "New Version". Each dropdown will be populated with the list of available code versions.
    -   By default, the latest two versions can be pre-selected.
    -   Once two versions are selected, the diff view will be rendered directly below the dropdowns within the modal.
3.  **Diff View:**
    -   The comparison will be displayed in a **side-by-side** format.
    -   Lines with additions, deletions, or modifications will be clearly highlighted with different background colors.

### Implementation Steps

1.  **Install Dependency:**
    ```bash
    npm install react-diff-viewer-continued
    ```

2.  **Modify `CodeDetail.tsx`:**
    -   Add a "Compare Versions" button to the UI.
    -   Implement state management for the comparison modal (e.g., `isModalOpen`).

3.  **Create `VersionDiffModal.tsx` Component:**
    -   Create a new component to encapsulate the modal logic.
    -   It will receive the list of all code versions as props.
    -   Manage the state for the two selected versions (`oldVersionId`, `newVersionId`).
    -   Fetch or retrieve the content of the two selected versions.
    -   Use the `<ReactDiffViewer>` component to render the comparison, passing the two code strings as `oldValue` and `newValue` props.

4.  **Integrate Modal:**
    -   Render `<VersionDiffModal>` within `CodeDetail.tsx` and control its visibility using the state.

---

## 3. Feature 2: Enhanced Code Editor

### Objective

To replace the basic `<textarea>` elements in `CodeCreate.tsx` and `CodeDetail.tsx` with a feature-rich code editor. This will provide a vastly superior code writing and reading experience.

### Proposed Library

-   **`@monaco-editor/react`**: A React wrapper for the Monaco Editor, which powers VS Code. It's powerful, widely used, and provides an excellent out-of-the-box experience with features like:
    -   Syntax highlighting (for Python and many other languages)
    -   IntelliSense (autocompletion)
    -   Find and replace
    -   Line numbers
    -   Code folding

### UI/UX Design

-   The existing `<textarea>` for code content in both the creation and detail views will be replaced by the Monaco Editor component.
-   The editor will be configured for the Python language by default.
-   The editor's height will be adjusted to fit the layout, ensuring it provides ample space for coding without cluttering the page.

### Implementation Steps

1.  **Install Dependencies:**
    ```bash
    npm install @monaco-editor/react monaco-editor
    ```

2.  **Modify `CodeDetail.tsx`:**
    -   Import the `Editor` component from `@monaco-editor/react`.
    -   Replace the `<textarea>` element with the `<Editor>` component.
    -   Configure the editor's props:
        -   `height`: Set a suitable height (e.g., "70vh").
        -   `language`: Set to `"python"`.
        -   `theme`: Choose a theme (e.g., `"vs-dark"` or `"light"`).
        -   `value`: Bind to the `codeContent` state.
        -   `onChange`: Update the `codeContent` state when the editor content changes.

3.  **Modify `CodeCreate.tsx`:**
    -   Apply the same changes as in `CodeDetail.tsx`, replacing the `<textarea>` with the configured `<Editor>` component.

4.  **(Optional) Webpack Configuration:**
    -   Monaco Editor can be resource-intensive. While `create-react-app` handles basic setup, further optimization might be needed for production builds if performance issues arise. This can be revisited later.

## 4. Task Checklist

-   [ ] **Feature 1 (Diff Viewer):**
    -   [ ] Install `react-diff-viewer-continued`.
    -   [ ] Add "Compare Versions" button in `CodeDetail.tsx`.
    -   [ ] Create and implement `VersionDiffModal.tsx`.
    -   [ ] Test diff functionality with various versions.

-   [ ] **Feature 2 (Monaco Editor):**
    -   [ ] Install `@monaco-editor/react`.
    -   [ ] Replace `<textarea>` in `CodeDetail.tsx` with Monaco Editor.
    -   [ ] Replace `<textarea>` in `CodeCreate.tsx` with Monaco Editor.
    -   [ ] Ensure editor is correctly configured for Python syntax.
    -   [ ] Test code editing and saving in both components.
