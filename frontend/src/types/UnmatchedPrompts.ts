export enum UnmatchedPromptsKeys {
    prompt_id = 'ID',
    prompt = 'mensaje',
    created_at = 'Creado',
}

export type UnmatchedPrompt = {
    prompt_id: string
    prompt: string
    created_at: string
}
