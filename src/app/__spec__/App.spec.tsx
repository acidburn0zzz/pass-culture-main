import { render, screen } from "@testing-library/react"
import React from "react"

import * as pcapi from "repository/pcapi/pcapi"

import App from "../App"

jest.mock("utils/config", () => ({
  APP_SEARCH_ENDPOINT: "app-search-endpoint",
  APP_SEARCH_KEY: "app-search-key",
}))

jest.mock("repository/pcapi/pcapi", () => ({
  authenticate: jest.fn(),
}))

describe("app", () => {
  describe("when is authenticated", () => {
    beforeEach(() => {
      pcapi.authenticate.mockResolvedValue()
    })

    it("should show search offers input", async () => {
      // When
      render(<App />)

      // Then
      const pageTitle = screen.getByRole("heading", { level: 1 })
      expect(pageTitle).toHaveTextContent("pass Culture")
      const contentTitle = await screen.findByText("Rechercher une offre", {
        selector: "h2",
      })
      expect(contentTitle).toBeInTheDocument()
      expect(screen.getByRole("textbox")).toBeInTheDocument()
    })
  })

  describe("when is not authenticated", () => {
    beforeEach(() => {
      pcapi.authenticate.mockRejectedValue()
    })

    it("should tell user that he is not authorized to access this page", async () => {
      // When
      render(<App />)

      // Then
      const pageTitle = screen.getByRole("heading", { level: 1 })
      expect(pageTitle).toHaveTextContent("pass Culture")
      const contentTitle = await screen.findByText(
        "Vous n'êtes pas autorisé à accéder à cette page",
        { selector: "h2" }
      )
      expect(contentTitle).toBeInTheDocument()
      expect(screen.queryByRole("textbox")).not.toBeInTheDocument()
    })
  })
})
