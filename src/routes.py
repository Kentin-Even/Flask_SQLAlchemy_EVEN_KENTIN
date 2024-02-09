from flask import Blueprint, render_template
from .database import db
from .models import Chambre, Client, Reservation
from flask import jsonify, request

main = Blueprint('main', __name__)


# get chamebres disponibles avec date_arrivee et date_depart
@main.route('/api/chambres/disponibles', methods=['GET'])
def chambres_disponibles():
  date_arrivee_str = request.args.get('date_arrivee')
  date_depart_str = request.args.get('date_depart')
    
  if not date_arrivee_str or not date_depart_str:
    return jsonify({'error': 'Les paramètres date_arrivee et date_depart sont nécessaires.'}), 400

  try:
    date_arrivee = datetime.strptime(date_arrivee_str, '%Y-%m-%d')
    date_depart = datetime.strptime(date_depart_str, '%Y-%m-%d')
  except ValueError:
    return jsonify({'error': 'Format de date invalide. Utilisez le format YYYY-MM-DD.'}), 400

  chambres_disponibles = []
  chambres_occupees = set()
  reservations = Reservation.query.filter(Reservation.date_arrivee <= date_depart, Reservation.date_depart >= date_arrivee).all()
  for reservation in reservations:
    chambres_occupees.add(reservation.id_chambre)

  toutes_les_chambres = Chambre.query.all()
  for chambre in toutes_les_chambres:
    if chambre.id not in chambres_occupees:
      chambres_disponibles.mainend({
        'id': chambre.id,
        'numero': chambre.numero,
        'type': chambre.type,
        'prix': float(chambre.prix)
      })

  return jsonify(chambres_disponibles)

# réserver une chambre avec l'id du client, id de la chambre, date arrivé et date départ  
@main.route('/api/reservations', methods=['POST'])
def creer_reservation():
  id_client = data.get('id_client')
  id_chambre = data.get('id_chambre')
  date_arrivee_str = data.get('date_arrivee')
  date_depart_str = data.get('date_depart')

  if not id_client or not id_chambre or not date_arrivee_str or not date_depart_str:
    return jsonify({'error': 'Toutes les données (id_client, id_chambre, date_arrivee, date_depart) sont nécessaires.'}), 400

  try:
    date_arrivee = datetime.strptime(date_arrivee_str, '%Y-%m-%d')
    date_depart = datetime.strptime(date_depart_str, '%Y-%m-%d')
  except ValueError:
    return jsonify({'error': 'Format de date invalide. Utilisez le format YYYY-MM-DD.'}), 400

  reservations_existantes = Reservation.query.filter_by(id_chambre=id_chambre).all()
  for reservation in reservations_existantes:
    if date_arrivee < reservation.date_depart and date_depart > reservation.date_arrivee:
      return jsonify({'error': 'La chambre est déjà réservée pour les dates demandées.'}), 400

  nouvelle_reservation = Reservation(id_client=id_client, id_chambre=id_chambre, date_arrivee=date_arrivee, date_depart=date_depart, statut='confirmée')
  db.session.add(nouvelle_reservation)
  db.session.commit()

  # envoyer un   
  return jsonify({'success': True, 'message': 'Réservation créée avec succès.'})

@main.route('/api/reservations/<int:id>', methods=['DELETE'])
def annuler_reservation(id):
  reservation = Reservation.query.get(id)

  if not reservation:
    return jsonify({'error': 'Réservation non trouvée.'}), 404

  db.session.delete(reservation)
  db.session.commit()

  return jsonify({'success': True, 'message': 'Réservation annulée avec succès.'})

@main.route('/api/chambres', methods=['POST'])
def ajouter_chambre():
  numero = data.get('numero')
  type_chambre = data.get('type')
  prix = data.get('prix')

  if not numero or not type_chambre or not prix:
      return jsonify({'error': 'Toutes les données (numero, type, prix) sont nécessaires.'}), 400

  nouvelle_chambre = Chambre(numero=numero, type=type_chambre, prix=prix)
  db.session.add(nouvelle_chambre)
  db.session.commit()

  return jsonify({'success': True, 'message': 'Chambre ajoutée avec succès.'})

@main.route('/api/chambres/<int:id>', methods=['PUT'])
def modifier_chambre(id):
  chambre = Chambre.query.get(id)

  if not chambre:
      return jsonify({'error': 'Chambre non trouvée.'}), 404

  chambre.numero = data.get('numero', chambre.numero)
  chambre.type = data.get('type', chambre.type)
  chambre.prix = data.get('prix', chambre.prix)
  db.session.commit()

  return jsonify({'success': True, 'message': 'Chambre mise à jour avec succès.'})


@main.route('/api/chambres/<int:id>', methods=['DELETE'])
def supprimer_chambre(id):
  chambre = Chambre.query.get(id)

  if not chambre:
    return jsonify({'error': 'Chambre non trouvée.'}), 404

  db.session.delete(chambre)
  db.session.commit()

  return jsonify({'success': True, 'message': 'Chambre supprimée avec succès.'})
