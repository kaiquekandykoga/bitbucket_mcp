# frozen_string_literal: true

module BitbucketMcp
  # Helpers for building JSON Schema property fragments used by tool input
  # schemas. Keeping these in one place makes the 300+ tool definitions concise
  # and consistent.
  module Schema
    module_function

    # A string property.
    def str(description) = { type: "string", description: description }

    # An integer property.
    def int(description) = { type: "integer", description: description }

    # A boolean property.
    def bool(description) = { type: "boolean", description: description }

    # An array-of-strings property.
    def strs(description) = { type: "array", items: { type: "string" }, description: description }

    # A free-form array property (items may be objects or any type). Use for
    # parameters whose elements are objects, e.g. lists of annotations.
    def array(description) = { type: "array", description: description }

    # A free-form object property (arbitrary nested shape). Use for structured
    # parameters whose shape is documented in the description.
    def object(description) = { type: "object", description: description }

    # An object mapping string keys to string values (e.g. filename => contents).
    def str_map(description) = { type: "object", additionalProperties: { type: "string" }, description: description }

    # Shared properties that appear across most endpoints.
    WORKSPACE = str("Bitbucket workspace slug (the team or user that owns the repository).").freeze
    REPOSITORY = str("Repository slug.").freeze
    PAGE = int("1-based page number for paginated results.").freeze
    PAGELEN = int("Number of items to return per page.").freeze
  end
end
