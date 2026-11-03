"""Matrice delle policy (livello 11).

TODO (passo 5): scrivi qui UN test parametrizzato (@pytest.mark.parametrize) che copre
ogni ruolo per ogni azione delle policy di boards/policies.py:
  ruoli: owner, collaborator, stranger, anonymous (AnonymousUser)
  azioni: view (can_view_board), edit (can_edit_board), add_collaborator (can_add_collaborator)
Almeno 12 casi, con id leggibili che contengono il ruolo (es. 'owner-view').
Usa le fixture di conftest (owner, collaborator, stranger, board): niente create_user qui.
"""